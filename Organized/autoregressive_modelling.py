import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from scipy import linalg

class Autoregressive:
    def __init__(self, coefficients, number_samples):
        self.noise = np.random.normal(0, 1, size = number_samples)
        self.coefficients = coefficients

        # Filter the noise signal using the AR Coefficients
        # This signal will be our data
        self.x = self.filter()

        # Afterwards, compute sample correlation and estimate the AR coefficients of the process
        self.sample_correlation = self.autocorrelation_function()
        self.estimated_coefficients = self.yule_walker(model_order = 5)

        print("True coefficients:")
        print(self.coefficients)
        print("Estimated coefficients:")
        print(self.estimated_coefficients)

        # Use the estimated AR coefficients to evaluate the estimated model. Compute prediction array, error vector, and error mean
        self.predicted = self.prediction(self.estimated_coefficients)
        self.predicted_dynamic = self.dynamic_prediction(self.estimated_coefficients)

        self.prediction_error = self.calculate_prediction_error(self.predicted)
        self.prediction_error_dynamic = self.calculate_prediction_error(self.predicted_dynamic)

        self.prediction_error_variance = self.calculate_prediction_error_variance(self.prediction_error)
        self.prediction_error_dynamic_variance = self.calculate_prediction_error_variance(self.prediction_error_dynamic)

        print("Mean of prediction_error: {} | Mean of prediction_error_dynamic: {}".format(self.calculate_prediction_error_mean(self.prediction_error), self.calculate_prediction_error_mean(self.prediction_error_dynamic)))
        print("Variance of prediction_error: {} | Variance of prediction_error_dynamic: {}".format(self.prediction_error_variance, self.prediction_error_dynamic_variance))

        self.plotter()

    def filter(self):
        self.filter_numerator = [1]
        self.filter_denominator = [1, -1.35, 0.94, -0.48, 0.04, 0.17]

        zi = scipy.signal.lfilter_zi(self.filter_numerator, self.filter_denominator)
        x, _ = scipy.signal.lfilter(self.filter_numerator, self.filter_denominator, self.noise, zi = zi*self.noise[0])

        return x

    def autocorrelation_function(self):
        result = np.correlate(self.x, self.x, mode = 'full')
        result = result[result.size//2:]
        max_index = np.argmax(result)

        if max_index != 0:
            print("Maximum of Autocorrelation function not in 0!")

        return result/result[max_index]

    def yule_walker(self, model_order):
        print(self.sample_correlation[0:6])
        # Estimation of R Matrix:
        R_matrix = linalg.toeplitz(self.sample_correlation[0:model_order])
        print(R_matrix)

        # Estimation of r Matrix:
        r_matrix = self.sample_correlation[1:model_order + 1]
        print(r_matrix)

        # Solve Yule Walker Equation
        ar_coefficients = linalg.inv(R_matrix).dot(r_matrix)

        return ar_coefficients

    def prediction(self, ar_coef):
        # Use AR Coefficients and real samples to generate new samples
        model_order = len(ar_coef)

        predicted = np.zeros(len(self.x))
        predicted[0:model_order] = self.x[0:model_order]

        inversed_coef = list(reversed(ar_coef)) #Just to ease computations

        for i in range(model_order, len(self.x)):
            predicted[i] = (inversed_coef*self.x[i-model_order:i]).sum()

        return predicted

    def dynamic_prediction(self, ar_coef):
        # Use AR Coefficients and predictions to generate new samples
        model_order = len(ar_coef)

        predicted = np.zeros(len(self.x))
        # Copy the first "model_order" samples just to get things going
        predicted[0:model_order] = self.x[0:model_order]

        inversed_coef = list(reversed(ar_coef))

        for i in range(model_order, len(self.x)):
            predicted[i] = (inversed_coef * predicted[i-model_order:i]).sum()

        return predicted

    def calculate_prediction_error(self, prediction_array):
        return self.x - prediction_array

    def calculate_prediction_error_mean(self, prediction_error):
        return prediction_error.sum()/len(prediction_error)

    def calculate_prediction_error_variance(self, prediction_error):
        mean = self.calculate_prediction_error_mean(prediction_error)
        difference = prediction_error - mean
        squared = difference**2

        return squared.sum()/(len(squared) - 1)

    def plotter(self):
        signals = True
        autocorrelation = True
        ar_parameters = True
        estimations = True
        prediction_errors = True

        if signals:
            plt.figure()
            plt.title("Original vs Filtered signal")
            plt.plot(self.x, color='red', label="signal")
            plt.plot(self.noise, label = "noise")
            plt.legend()

        if autocorrelation:
            plt.figure()
            plt.plot(self.sample_correlation)
            plt.title("Sample Autocorrelation")

        if ar_parameters:
            plt.figure()
            plt.title("AR Model Parameters")
            plt.plot(self.estimated_coefficients, '.', label = 'estimated_coefficients')
            plt.plot(self.coefficients, '.', label = 'true_coefficients')


        if estimations:
            plt.figure()
            plt.plot(self.x, label = "data")
            plt.plot(self.predicted, label = "predicted")
            plt.plot(self.predicted_dynamic, label = "predicted_dynamically")
            plt.title("Evaluation of Estimated models")
            plt.legend()

        if prediction_errors:
            plt.figure()
            plt.title("Prediction Errors")
            plt.plot(self.noise, label = "original_noise")
            plt.plot(self.prediction_error, label = 'prediction_error')
            plt.plot(self.prediction_error_dynamic, label = 'prediction_error_dynamic')
            plt.legend()

        plt.show()

if __name__ == "__main__":
    ar_process_coefficients = [1.35, -0.94, 0.48, -0.04, -0.17]
    ar = Autoregressive(ar_process_coefficients, 1000)

