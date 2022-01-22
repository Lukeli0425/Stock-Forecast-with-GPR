import numpy as np
import pandas as pd
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF  # squared exponential kernel
from sklearn.gaussian_process.kernels import *
import data_handler


class Wrapper:
    __company_data = None
    __prices_data = None
    __max_days = None
    __alpha = None
    __iterations = None
    __kernels = None
    __gp = None

    def __init__(self, company_name: str):
        self.__company_data = data_handler.CsvHandler(company_name)  # 读取公司数据
        self.__prices_data = self.__company_data.get_equal_length_prices()  # 获得各个年份的数据
        self.__max_days = self.__company_data.max_days  # 开盘天数252天

        # 协方差函数
        # kernel = 63 * RBF(length_scale=1) 
        kernel = 17 * ExpSineSquared(length_scale=1)  
        self.__iterations = 20  # 迭代次数

        self.__alpha = 1e-10  
        self.__kernels = [kernel]
        self.__gp = GaussianProcessRegressor(kernel=self.__kernels[0], alpha=self.__alpha,
                                             n_restarts_optimizer=self.__iterations,
                                             normalize_y=False)

    def get_eval_model(self,
                       start_year: int,
                       end_year: int,
                       pred_year: int,
                       pred_quarters: list = None):
        years_quarters = list(range(start_year, end_year + 1)) + ['Quarter']
        training_years = years_quarters[:-2]  # 取到倒数第二个数

        # 这一句的意思是只取到years_quarters索引范围内的数据
        # df_prices = self.__prices_data
        df_prices = self.__prices_data[self.__prices_data.columns.intersection(years_quarters)]
        possible_days = list(df_prices.index.values)  # 这是取了读取的数据的所有索引的数值(即开盘天数0,1,2,3...,251这样的)

        # XY初始化的时候里面的数据是随机的,相当于构造了两个形状和数据类型确定的空数组
        X = np.empty([1, 2], dtype=int)
        Y = np.empty([1], dtype=float)

        first_year_prices = df_prices[start_year]
        if start_year == self.__company_data.years[0]:
            first_year_prices = first_year_prices[first_year_prices.iloc[:] != 0]  # 这里不取第一个数的原因是在预处理的时候已经将第一个数置零
            first_year_prices = (pd.Series([0.0], index=[first_year_prices.index[0]-1])).append(first_year_prices)
            # ???这一步莫名其妙

        first_year_days = list(first_year_prices.index.values)  # 第一年的数据
        first_year_X = np.array([[start_year, day] for day in first_year_days])  # 构造[[2008, 1],[2008, 2]...[2008, 251]]
        # print(first_year_X)

        X = first_year_X
        Y = np.array(first_year_prices)  # 第一年的股票价格数组
        # print(Y)
        for current_year in training_years[1:]:
            current_year_prices = list(df_prices.loc[:, current_year])
            current_year_X = np.array([[current_year, day] for day in possible_days])
            X = np.append(X, current_year_X, axis=0)
            Y = np.append(Y, current_year_prices)

        last_year_prices = df_prices[end_year]
        last_year_prices = last_year_prices[last_year_prices.iloc[:].notnull()]

        last_year_days = list(last_year_prices.index.values)
        if pred_quarters is not None:
            length = 63 * (pred_quarters[0] - 1)
            last_year_days = last_year_days[:length]
            last_year_prices = last_year_prices[:length]
        last_year_X = np.array([[end_year, day] for day in last_year_days])

        X = np.append(X, last_year_X, axis=0)
        Y = np.append(Y, last_year_prices)

        if pred_quarters is not None:
            pred_days = [day for day in
                         range(63 * (pred_quarters[0]-1), 63 * pred_quarters[int(len(pred_quarters) != 1)])]
        else:
            pred_days = list(range(0, self.__max_days))
        x_mesh = np.linspace(pred_days[0], pred_days[-1]
                             , 2000)
        x_pred = ([[pred_year, x_mesh[i]] for i in range(len(x_mesh))])

        self.__gp = self.__gp.fit(X, Y) # train
        self.__kernels.append(self.__gp.kernel_) # save model
        y_mean, y_cov = self.__gp.predict(x_pred, return_cov=True) # predict
        return x_mesh, y_mean, y_cov

    def get_kernels(self):
        return self.__kernels
