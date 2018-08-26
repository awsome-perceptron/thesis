import global_variables as gv
import numpy as np
import pandas as pd
import time
from scipy import signal, linalg
from math import log, pow, ceil
from statsmodels.tsa.ar_model import AR
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
import pickle


class Task:
    def __init__(self, task_name, duration, task_data, task_indexes, fast_performance, folder):
        self.folder = folder
        self.name = task_name
        self.duration = duration
        self.task_data = task_data
        self.task_indexes = task_indexes

        # Create feature objects
        self.actigraphy = Actigraphy(self, fast_performance)
        self.heart = Heart(self.task_data["BVP"], self.task_data["HR"])
        self.temperature = Temperature(self.task_data["TEMP"])
        self.eda = Eda(self.task_data["EDA"])

        self.task_features = {}

    def build_task_features(self):
        features = dict()
        features['task_name'] = self.name
        features['duration'] = self.duration
        features['acc'] = self.actigraphy.actigraphy_features()
        features['heart'] = self.heart.heart_features()
        features['temp'] = self.temperature.temperature_features()
        features['eda'] = self.eda.eda_features()

        self.task_features = features


class Actigraphy:
    def __init__(self, master, fast_performance):
        self.master = master
        self.sample_rate = 32

        self.raw = master.task_data["ACC_RAW"]
        self.raw_detrended = master.task_data["ACC_DETRENDED"]
        self.magnitude = master.task_data["ACC_MAG"]
        self.raw_means = master.task_data["ACC_RAW_MEANS"]

        # Basic statistic features calculation: Mean, Variance, Standard Deviation and Total Variation
        self.magnitude_mean = self.calculate_magnitude_mean()
        self.magnitude_detrended = self.magnitude - self.magnitude_mean
        self.max = float(self.magnitude_detrended.max())
        self.min = float(self.magnitude_detrended.min())

        self.variance = self.calculate_sample_variance()
        self.standard_deviation = self.calculate_standard_deviation()
        self.total_variation = self.calculate_total_variation()

        # PSD Estimation: 2 approaches
        # 1) Periodogram calculation
        self.freq, self.P_dens = self.calculate_periodogram()

        # 2) Autoregressive Modeling
        if fast_performance:
            self.yule_walker = None
        else:
            self.yule_walker = YuleWalker(self.master, self.magnitude_detrended)

    def calculate_magnitude_mean(self):
        # Method: Sum all magnitude samples and divide by N
        return self.magnitude.sum()/len(self.magnitude)

    def calculate_sample_variance(self):
        # Method:
        # 1)Subtract average of magnitude mean to each magnitude sample - It's already a class attribute
        # 2) Square the result and then calculate the average

        squared = self.magnitude_detrended**2

        return squared.sum()/(len(squared) - 1)

    def calculate_standard_deviation(self):
        # Method: Square the result from variance

        return np.sqrt(self.variance)

    def calculate_total_variation(self):
        # Method: Calculate total variance of actigraphy magnitude signal
        # 1) Build original data - Ignore last point
        # 2) Build shifted data: Advance each sample by one unit

        shifted_magnitude = self.magnitude.shift(periods = -1, freq = None, axis = 0)

        difference_vector = abs(shifted_magnitude - self.magnitude)

        return difference_vector.sum()

    def calculate_periodogram(self):
        f, p_dens = signal.periodogram(self.magnitude, self.sample_rate)

        return f, p_dens

    def actigraphy_features(self):
        features = {'mean': self.magnitude_mean, 'max': self.max, 'min': self.min,  'variance': self.variance, 'std': self.standard_deviation, 'tv': self.total_variation,
                    'energy_bands': self.yule_walker.energy_bands, 'order': self.yule_walker.model_order, 'mse': self.yule_walker.mse_statsmodel,
                    'aic': self.yule_walker.aic_statsmodel, 'prediction_error_mean': self.yule_walker.prediction_e_statsmodel_mean}

        return features


class Heart:
    def __init__(self, bvp_data, hr_data):
        self.bvp = bvp_data
        self.hr = hr_data

        self.average_hr = self.calculate_average_heart_rate()
        self.maximum_hr = self.get_max_heart_rate()
        self.minimum_hr = self.get_min_heart_rate()
        self.max_min_difference = self.maximum_hr - self.minimum_hr

    def calculate_average_heart_rate(self):
        return float(self.hr.sum()/len(self.hr))

    def get_max_heart_rate(self):
        return float(self.hr.max())

    def get_min_heart_rate(self):
        return float(self.hr.min())

    def heart_features(self):
        features = {'mean': self.average_hr, 'max': self.maximum_hr, 'min': self.minimum_hr, 'max-min': self.max_min_difference}

        return features


class Temperature:
    def __init__(self, temperature_data):
        self.temp = temperature_data

        self.max_temp = self.get_maximum_temp()
        self.min_temp = self.get_minimum_temp()
        self.mean_temp = self.temp.sum()/len(self.temp)

    def get_maximum_temp(self):
        return float(self.temp.max())

    def get_minimum_temp(self):
        return float(self.temp.min())

    def temperature_features(self):
        features = {'mean': float(self.mean_temp), 'max': self.max_temp, 'min': self.min_temp}

        return features


class Eda:
    def __init__(self, eda_data):
        self.eda = eda_data

        self.mean = self.eda.sum()/len(self.eda)
        self.maximum_eda = self.get_max_eda()
        self.minimum_eda = self.get_min_eda()

    def get_max_eda(self):
        return float(self.eda.max())

    def get_min_eda(self):
        return float(self.eda.min())

    def eda_features(self):
        features = {'mean': float(self.mean), 'max': self.maximum_eda, 'min': self.minimum_eda}

        return features


class YuleWalker:
    def __init__(self, master, magnitude_detrended):
        print_important_variables = False

        self.master = master
        self.magnitude_detrended = magnitude_detrended

        # Calculate sample correlation
        self.sample_correlation = self.autocorrelation_function()

        # Calculate or load AR Coefficients
        self.AR_model = AR(self.magnitude_detrended)
        self.AR_model_fit = self.AR_model.fit(max_lag = 50, ic = 'aic')
        self.ar_coefficients = self.AR_model_fit.params
        self.model_order = len(self.ar_coefficients) - 1

        # EVALUATION OF AR MODELS
        # 1) Calculate prediction vector
        # self.prediction_v = self.calculate_prediction_vector(self.ar_coefficients, len(self.ar_coefficients))
        self.prediction_v_statsmodel = self.calculate_prediction_vector(self.AR_model_fit.params[1:], len(self.AR_model_fit.params) - 1, self.AR_model_fit.params[0])

        # 2) Calculate prediction error
        # self.prediction_e = self.calculate_prediction_error(self.prediction_v)
        self.prediction_e_statsmodel = self.calculate_prediction_error(self.prediction_v_statsmodel)

        # 3) Calculate prediction error variance
        # self.prediction_variance = self.calculate_prediction_error_variance(self.prediction_v)
        self.prediction_variance_statsmodel = self.calculate_prediction_error_variance(self.prediction_v_statsmodel)

        # 4) Calculate mean squared error
        # self.mse = self.calculate_mean_squared_error(self.prediction_v)
        self.mse_statsmodel = mean_squared_error(self.magnitude_detrended, self.prediction_v_statsmodel)

        # 4) Calculate AIC
        # self.aic = self.akaike_information_criterion(len(self.magnitude_detrended), len(self.ar_coefficients), self.prediction_variance)
        self.aic_statsmodel = self.akaike_information_criterion(len(self.magnitude_detrended), len(self.AR_model_fit.params) - 1, self.prediction_variance_statsmodel)

        # 5) Check some error prediction properties - Eventually use it to test for whiteness or whatever (learn)
        # self.prediction_e_mean = self.calculate_prediction_error_mean(self.prediction_e)
        self.prediction_e_statsmodel_mean = self.calculate_prediction_error_mean(self.prediction_e_statsmodel)

        # Calculation of power spectral density using the AR Coefficients
        # self.freq, self.dens = self.calculate_spectrum(self.ar_coefficients)
        self.freq_statsmodel, self.dens_statsmodel = self.calculate_spectrum(self.AR_model_fit.params[1:])

        self.energy_bands = self.calculate_energy_bands()

        if print_important_variables:
            self.print_object_description()

    def autocorrelation_function(self):
        #Calculate Autocorrelation Function
        result = np.correlate(self.magnitude_detrended, self.magnitude_detrended, mode = 'full')
        result = result[result.size//2:]
        max_index = np.argmax(result)

        if max_index != 0:
            print("Autocorrelation Function - ArgMax: {} | Task: {}".format(max_index, self.master.name))

        # Normalize Autocorrelation so that maximum value is one
        return result/result[max_index]

        # return result/len(self.magnitude_detrended)

    def autocorrelation_coefficient(self, lag):
        # DEBUG ONLY - Calculate autocorrelation coefficient; Result should be the same of the autocorrelation function
        signal = self.magnitude_detrended
        shifted = signal.shift(periods = lag)
        product = signal*shifted
        return product.sum()/len(self.magnitude_detrended)

    def fitting(self, model_order):
        # Given a model order estimates coefficients based on Yule Walker Equation
        sample_correlation = self.sample_correlation

        # Estimation of R Matrix = (X^T * X)/N by autocorrelation function (I think it's possible to calculate based on the data samples)
        R_matrix = linalg.toeplitz(sample_correlation[0:model_order])

        # Estimation of r = (X^T * x)/N by autocorrelation function (I think it's possible to calculate based on the data samples)
        r_matrix = sample_correlation[1:model_order + 1]

        # Calculation of AR Coefficients based on Yule Walker Equation
        ar_coefficients = linalg.inv(R_matrix).dot(r_matrix)

        return ar_coefficients

    def autoregressive_statsmodel(self, max_lag):
        # Fits an autoregressive model to a time series; Automatically determines the best optimal lag
        self.training_set = self.magnitude_detrended

        # Call functions to fit the AR Model
        model = AR(self.training_set)
        model_fit = model.fit(maxlag = max_lag, ic = 'aic')

        return model, model_fit

    def calculate_prediction_vector(self, ar_coefficients, model_order, constant = None):
        predicted = np.zeros(len(self.magnitude_detrended))
        predicted[0:model_order] = self.magnitude_detrended[0:model_order]

        if constant is not None:
            # AR Model with constant term ( For AR models from statsmodels package)
            offset = constant
        else:
            # AR Model without constant term ( For AR models developed by our own)
            offset = 0

        # Reverse order of AR Coefficients for efficient computation
        reversed_coef = list(reversed(ar_coefficients))

        # Calculation of Prediction Vector elements
        for i in range(model_order, len(self.magnitude_detrended)):
            predicted[i] = offset + (reversed_coef*self.magnitude_detrended[i-model_order:i]).sum()

        return predicted

    def calculate_prediction_error(self, prediction_vector):
        return self.magnitude_detrended - prediction_vector

    def calculate_prediction_error_variance(self, prediction_error):
        mean = prediction_error.sum()/len(prediction_error)
        detrended = prediction_error - mean
        squared = detrended**2

        return squared.sum()/(len(prediction_error) - 1)

    def akaike_information_criterion(self, n_obs, model_order, prediction_error_variance):
        # Log function from math package with one argument, returns the natural logarithm
        return n_obs * log(prediction_error_variance) + 2 * model_order

    def calculate_prediction_error_mean(self, prediction_error):
        # Mean
        mean = prediction_error.sum()/len(prediction_error)

        return mean

    def calculate_spectrum(self, ar_coefficients):
        # Not sure why the expression for h_db is like that
        a = np.concatenate([np.ones(1), -ar_coefficients])
        w, h = signal.freqz(1, a)
        h_db = 10*np.log10(2*(np.abs(h)/len(h)))

        return w/np.pi, h_db

    def calculate_energy_bands(self):
        # Calculation of Spectral Energy by integration of the PSD Function. The PSD function has 512 points.
        # Trapezoidal approach. For each point, calculate the average between it and the next point and multiply for the delta frequency (fixed)
        # Low Band: 171 bins
        # Medium Band: 170 bins
        # High Band: 170 bins
        # Total bins: 511, because of the shift operation

        h_linear = pd.DataFrame(np.power(10, self.dens_statsmodel/10))
        h_linear_shifted = h_linear.shift(periods=-1)
        avg = (h_linear + h_linear_shifted)/2

        points_per_band = int(len(h_linear)/3) # 170
        delta_f = 1/len(h_linear)*np.pi

        low_energy = avg[0:points_per_band+1].sum()*delta_f #171
        medium_energy = avg[points_per_band+1:2*points_per_band+1].sum()*delta_f #170
        high_energy = avg[2*points_per_band+1:-1].sum()*delta_f #170

        return [low_energy, medium_energy, high_energy]

    def print_object_description(self):
        print(" --------------------------- Task: {} -------------------------------- ".format(self.master.name))
        print("Mean of Detrended Magnitude: {}".format(self.magnitude_detrended.sum()/len(self.magnitude_detrended)))
        print("Model Order -  Statsmodel: {}".format(len(self.ar_coefficients) - 1))
        print("Variance of prediction error - Statsmodel: {}".format(self.prediction_variance_statsmodel))
        print("Mean of prediction error - Statsmodel: {}".format( self.prediction_e_statsmodel_mean))
        print("Mean Squared Error: Statsmodel: {}".format(self.mse_statsmodel))
        print("AIC - Statsmodel: {}".format(self.aic_statsmodel))
        print("\n")

