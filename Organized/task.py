import global_variables as gv
import numpy as np
import time
from scipy import signal, linalg
from math import log
from statsmodels.tsa.ar_model import AR
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error

class Task:
    def __init__(self, task_name, duration, task_data, task_indexes, actigraphy_mean_vector):
        self.name = task_name
        self.duration = duration
        self.task_data = task_data
        self.task_indexes = task_indexes

        #Calculate features for each signal
        self.actigraphy_features = ActigraphyFeatures(self)
        self.heart_features = HeartFeatures(self.task_data["BVP"], self.task_data["HR"])
        self.temperature_features = TemperatureFeatures(self.task_data["TEMP"])
        self.eda_features = EdaFeatures(self.task_data["EDA"])

        #print("Task: {} | Magnitude Mean: {} | Variance: {} | SD: {} | TV: {}".format(self.name, self.actigraphy_features.magnitude_mean,
                               #                                              self.actigraphy_features.variance,
                                #                                  self.actigraphy_features.standard_deviation, self.actigraphy_features.total_variation))
        #print("Average HR: {} | Max HR: {} | Min HR: {} | Max - Min: {}".format(self.heart_features.average_hr, self.heart_features.maximum_hr,
                                 #                                               self.heart_features.minimum_hr, self.heart_features.max_min_difference))


class ActigraphyFeatures:
    def __init__(self, master):
        self.sample_rate = 32
        self.master = master

        self.raw = master.task_data["ACC_RAW"]
        self.detrended = master.task_data["ACC_DETRENDED"]
        self.magnitude = master.task_data["ACC_MAG"]
        self.magnitude_alternative = master.task_data["ACC_MAG_ALT"]
        self.raw_mean_vector = master.task_data["ACC_MEANS"]

        # Basic statistic features calculation: Mean, Variance, Standard Deviation and Total Variation
        self.magnitude_mean = self.calculate_magnitude_mean()
        self.magnitude_detrended = self.magnitude - self.magnitude_mean
        self.variance = self.calculate_sample_variance()
        self.standard_deviation = self.calculate_standard_deviation()
        self.total_variation = self.calculate_total_variation()

        #Calculate fft
        self.fft = self.calculate_fft()

        # PSD Estimation: 2 Approaches - By Periodogram or Univariate Autoregressive Spectral Analysis
        # Periodogram calculation
        self.freq, self.P_dens = self.calculate_periodogram()

        # Autoregressive Modeling
        self.yule_walker = YuleWalker(self.master, self.magnitude_detrended, self.magnitude_mean)

    def calculate_magnitude_mean(self):
        # Method: Sum all magnitude samples and divide by N
        return self.magnitude.sum()/len(self.magnitude)

    def calculate_sample_variance(self):
        # Method:
        # 1)Subtract average of magnitude mean to each magnitude sample
        # 2) Square the result and then calculate the average

        detrended_magnitude = self.magnitude - self.magnitude_mean
        squared = detrended_magnitude**2

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

    def calculate_fft(self):
        fft = {}
        signal = self.magnitude

        fft['original'] = {'values': np.fft.rfft(signal)/self.sample_rate, 'freq_axis': np.fft.rfftfreq(len(signal))*self.sample_rate}

        window = np.blackman(signal.size)
        windowed_data = signal * window

        fft['filtered'] = {'values': np.fft.rfft(windowed_data)*self.sample_rate, 'freq_axis': np.fft.rfftfreq(len(windowed_data))*self.sample_rate}

        return fft

    def calculate_periodogram(self):
        f, p_dens = signal.periodogram(self.magnitude, self.sample_rate)

        return f, p_dens


class HeartFeatures:
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


class TemperatureFeatures:
    def __init__(self, temperature_data):
        self.temp = temperature_data

        self.maximum_temp = self.get_maximum_temp()
        self.minimum_temp = self.get_minimum_temp()

    def get_maximum_temp(self):
        return float(self.temp.max())

    def get_minimum_temp(self):
        return float(self.temp.min())


class EdaFeatures:
    def __init__(self, eda_data):
        self.eda = eda_data

        self.maximum_eda = self.get_max_eda()
        self.minimum_eda = self.get_min_eda()

    def get_max_eda(self):
        return float(self.eda.max())

    def get_min_eda(self):
        return float(self.eda.min())


class YuleWalker:
    def __init__(self, master, magnitude_detrended, mean):
        print_important_variables = False

        self.master = master
        self.magnitude_detrended = magnitude_detrended
        self.mean = mean

        # Fitting an AR Model using our functions
        self.sample_correlation = self.autocorrelation_function()
        self.ar_coefficients = self.fitting(model_order = 20)

        # Fitting an AR Model using developed package from statsmodel
        self.train_length = len(self.magnitude_detrended)
        self.AR_model, self.AR_model_fit = self.autoregressive_statsmodel(self.train_length)

        # EVALUATION OF AR MODELS
        # 1) Calculate prediction vector
        self.prediction_v = self.calculate_prediction_vector(self.ar_coefficients, len(self.ar_coefficients))
        self.prediction_v_statsmodel = self.calculate_prediction_vector(self.AR_model_fit.params[1:], len(self.AR_model_fit.params) - 1, self.AR_model_fit.params[0])

        # 2) Calculate prediction error
        self.prediction_e = self.calculate_prediction_error(self.prediction_v)
        self.prediction_e_statsmodel = self.calculate_prediction_error(self.prediction_v_statsmodel)

        # 3) Calculate prediction error variance
        self.prediction_variance = self.calculate_prediction_error_variance(self.prediction_v)
        self.prediction_variance_statsmodel = self.calculate_prediction_error_variance(self.prediction_v_statsmodel)

        # 4) Calculate mean squared error
        self.mse = self.calculate_mean_squared_error(self.prediction_v)
        self.mse_statsmodel = self.calculate_mean_squared_error(self.prediction_v_statsmodel)

        # 4) Calculate AIC
        self.aic = self.akaike_information_criterion(len(self.magnitude_detrended), len(self.ar_coefficients), self.prediction_variance)
        self.aic_statsmodel = self.akaike_information_criterion(len(self.magnitude_detrended), len(self.AR_model_fit.params) - 1, self.prediction_variance_statsmodel)

        # 5) Check some error prediction properties
        self.prediction_e_mean = self.calculate_prediction_error_mean(self.prediction_e)
        self.prediction_e_statsmodel_mean = self.calculate_prediction_error_mean(self.prediction_e_statsmodel)

        self.freq, self.dens = self.calculate_spectrum(self.ar_coefficients)
        self.freq_statsmodel, self.dens_statsmodel = self.calculate_spectrum(self.AR_model_fit.params[1:])

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
        # Calculate autocorrelation coefficient; Use as debug only; Result should be the same of the autocorrelation function
        signal = self.magnitude_detrended
        shifted = signal.shift(periods = lag)
        product = signal*shifted
        return product.sum()/len(self.magnitude_detrended)

    def fitting(self, model_order):
        sample_correlation = self.sample_correlation

        # Estimation of R Matrix = (X^T * X)/N by autocorrelation function (I think it's possible to calculate based on the data samples)
        R_matrix = linalg.toeplitz(sample_correlation[0:model_order])

        # Estimation of r = (X^T * x)/N by autocorrelation function (I think it's possible to calculate based on the data samples)
        r_matrix = sample_correlation[1:model_order + 1]

        # Calculation of AR Coefficients based on Yule Walker Equation
        ar_coefficients = linalg.inv(R_matrix).dot(r_matrix)

        return ar_coefficients

    def autoregressive_statsmodel(self, training_length):
        # Fits an autoregressive model to a time series; Automatically determines the best optimal lag
        self.training_set = self.magnitude_detrended[0:training_length]
        self.testing_set = self.magnitude_detrended[training_length:]

        model = AR(self.training_set)
        model_fit = model.fit(maxlag = 50, ic = 'aic')

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

    def calculate_mean_squared_error(self, prediction_vector):

        return mean_squared_error(self.magnitude_detrended, prediction_vector)

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

    def print_object_description(self):
        print(" --------------------------- Task: {} -------------------------------- ".format(self.master.name))
        print("Mean of Detrended Magnitude: {}".format(self.mean))
        print("Model Order - Mine: {} | Statsmodel: {}".format(len(self.ar_coefficients), len(self.AR_model_fit.params) - 1))
        print("Variance of prediction error - Mine: {} | Statsmodel: {}".format(self.prediction_variance, self.prediction_variance_statsmodel))
        print("Mean of prediction error - Mine: {} | Statsmodel: {}".format(self.prediction_e_mean, self.prediction_e_statsmodel_mean))
        print("Mean Squared Error: Mine: {} | Statsmodel: {}".format(self.mse, self.mse_statsmodel))
        print("AIC - Mine: {} | Statsmodel: {}".format(self.aic, self.aic_statsmodel))
        print("\n")
