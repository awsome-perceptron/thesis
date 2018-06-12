import global_variables as gv
import numpy as np

class Task:
    def __init__(self, task_name, duration, task_data, task_indexes, actigraphy_mean_vector):
        self.name = task_name
        self.duration = duration
        self.task_data = task_data
        self.task_indexes = task_indexes

        #Calculate features for each signal
        self.actigraphy_features = ActigraphyFeatures(self.task_data["ACC_MAG"], self.task_data["ACC"], actigraphy_mean_vector)
        self.heart_features = HeartFeatures(self.task_data["BVP"], self.task_data["HR"])
        self.temperature_features = TemperatureFeatures(self.task_data["TEMP"])
        self.eda_features = EdaFeatures(self.task_data["EDA"])

        print(" ------------------------------ ")
        print("Task: {} | Magnitude Mean: {} | Variance: {} | SD: {} | TV: {}".format(self.name, self.actigraphy_features.magnitude_mean,
                                                                             self.actigraphy_features.variance,
                                                                  self.actigraphy_features.standard_deviation, self.actigraphy_features.total_variation))

        print("Average HR: {} | Max HR: {} | Min HR: {} | Max - Min: {}".format(self.heart_features.average_hr, self.heart_features.maximum_hr,
                                                                                self.heart_features.minimum_hr, self.heart_features.max_min_difference))


    def set_task_indexes(self, task_indexes):
        #deprecated
        self.task_indexes = task_indexes


class ActigraphyFeatures:
    def __init__(self, actigraphy_magnitude, actigraphy_detrended, mean_vector):
        self.magnitude = actigraphy_magnitude
        self.detrended = actigraphy_detrended
        self.mean_vector = mean_vector
        # maybe add raw data here

        self.magnitude_mean = self.calculate_magnitude_mean()
        self.variance = self.calculate_sample_variance()
        self.standard_deviation = self.calculate_standard_deviation()
        self.total_variation = self.calculate_total_variation()

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

    def calculate_power_spectral_density(self):
        pass


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

