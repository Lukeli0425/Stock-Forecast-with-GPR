import pandas as pd
import numpy as np

class CsvHandler:
    df = None  # DataFrame, 其形状以Data中csv图形为标准
    quarters = None  # 季度
    years = None  # 年份
    max_days = None  # 最大天数(默认一年开盘天数为252天)

    def __init__(self, csv_name: str):  # python 双下划綫的意义是其不能被重写
        self.__load_data(csv_name)
        self.df['Norm Close'] = self.__add_normalized_data(self.df)
        self.df['Quarter'] = self.__add_quarters(self.df)
        self.max_days = 252  # 默认一年开市天数为252天

    def get_equal_length_prices(self, normalized=True):  # 这里的equal_length的意思是maxdays x 1维度
        df = self.__shift_first_year_prices()  # 先获得第一年的数据(maxdays x 1)维度
        for i in range(1, len(self.years)):
            df = pd.concat([df, pd.DataFrame(self.get_year_data(year=self.years[i], normalized=normalized))], axis=1)
            # axis = 1 各年的数据沿列延拓(默认是沿行延拓)
        df = df[:self.max_days]  # 只取到各年的Max_days以前的数据

        quarters = []  # 季度，注意这个quarters是局部变量，不是self.quarters
        for j in range(0, len(self.quarters)):
            for i in range(0, self.max_days // 4):  # python的/代表浮点数除法, //代表整形除法
                quarters.append(self.quarters[j])
        quarters = pd.DataFrame(quarters)  # 将quarters = ["Q1","Q1",..."Q2","Q2",...]转换为纵向的数表

        df = pd.concat([df, quarters], axis=1)   # 将各年数据与quarters纵向排列(这里可能出现对齐问题?)
        df.columns = self.years + ['Quarter']  # 标题要添加一个"Quarter"项
        df.index.name = 'Day'  # 沿行延拓的索引定义为’Day‘,与我们前面的分析是吻合的

        self.__fill_last_rows(df)  # 补行操作，确认数表格式

        return df

    # 这个函数的功能是获取当年的股票价格
    def get_year_data(self, year: int, normalized=True):
        if year not in self.years:
            raise ValueError('\n' + 
                             'Input year: {} not in available years: {}'.format(year, self.years))

        prices = (self.df.loc[self.df['Date'].dt.year == year])  # 获取当年的股票价格(返回的是一个数组)

        # 考察是否归一化，默认应该是需要归一化的。
        if normalized:
            return np.asarray(prices.loc[:, 'Norm Close'])
        else:
            return np.asarray(prices.loc[:, 'Close'])

    def get_whole_prices(self, start_year: int, end_year: int):
        if start_year < self.years[0] or end_year > self.years[-1]:
            raise ValueError('\n' +
                             'Input years out of available range! \n' +
                             'Max range available: {}-{}\n'.format(self.years[0], self.years[-1]) +
                             'Was: {}-{}'.format(start_year, end_year))

        df = (self.df.loc[(self.df['Date'].dt.year >= start_year) & (self.df['Date'].dt.year <= end_year)])
        df = df.loc[:, ['Date', 'Close']]

        return df

    def show(self, max_rows=None, max_columns=None):
        with pd.option_context('display.max_rows', max_rows, 'display.max_columns', max_columns):
            print(self.df)

    def __load_data(self, csv_name: str):
        # 获取csv文件数据并构造一个DataFrame(可以理解成一个多行Hash键值对，也可以理解成一个数表)
        self.df = pd.read_csv('./Data/' + csv_name + '.csv')  # 读取csv数据

        # 这句的意思是遍历数据csv文件的所有行，取其Date和Close两列
        self.df = self.df.iloc[:, [0, 4]]   # iloc函数用于处理从csv文件中提取的DataFrame

        # 去掉DataFrame中所有奇异数据
        self.df = self.df.dropna()

        # 将csv中的Date一列数据转换成日期
        self.df.Date = pd.to_datetime(self.df.Date)

        # 股票中的四个季度
        self.quarters = ['Q' + str(i) for i in range(1, 5)]  # quarters = [Q1, Q2, Q3, Q4]

    def __add_normalized_data(self, df):
        normalized = pd.DataFrame()  # 先构造一个空的数表

        self.years = list(df.Date)
        self.years = list({self.years[i].year for i in range(len(self.years))})  # 获得年份队列

        for i in range(0, len(self.years)):
            prices = self.get_year_data(year=self.years[i], normalized=False)  # 获得该年的股票价格数据
            mean = np.mean(prices)  # 取该年的数据的均值
            std = np.std(prices)  # 取该年数据的标准差
            prices = [(prices[i] - mean) / std for i in range(0, len(prices))]  # 获得标准化数据
            prices = [(prices[i] - prices[0]) for i in range(0, len(prices))]  # 减去第一个数据，偏置为0
            normalized = normalized.append(prices, ignore_index=True)  # 按列接入数据
        return normalized

    def __add_quarters(self, df):  # 加入季度数据(股票似乎特喜欢季度这个概念)
        quarters = pd.DataFrame()  # 空数阵

        for i in range(0, len(self.years)):
            # 第一个dates里只包含DF中year = years[i]那一年的第一列数据(第一列数据即时间)
            dates = list((df.loc[df['Date'].dt.year == self.years[i]]).iloc[:, 0])
            # print(dates)

            #
            dates = pd.DataFrame([self.__get_quarter(dates[i].month) for i in range(0, len(dates))])

            #
            quarters = quarters.append(dates, ignore_index=True)

        return quarters

    def __get_quarter(self, month: int):
        return self.quarters[(month - 1) // 3]  # 四个季度是0, 1, 2, 3

    def __shift_first_year_prices(self):
        prices = pd.DataFrame(self.get_year_data(self.years[0]))  # 获取第一年的股票价格数组
        df = pd.DataFrame([0 for _ in range(self.max_days - len(prices.index))])  # 这一行的功能是在已有数据的天数和最大天数之间添加0
        df = pd.concat([df, prices], ignore_index=True)  # 这一行是pandas的连接函数，将有数据的prices数组和无数据的df数组拼接起来
        # 这样保证了这一数组的维度是 MaxDays
        return df

    def __fill_last_rows(self, df):
        years = self.years[:-1]  # 取所有年

        for year in years:
            mean = np.mean(df[year])
            for i in range(self.max_days - 1, -1, -1):
                current_price = df.iloc[i, df.columns.get_loc(year)]
                if np.isnan(current_price):
                    df.iloc[i, df.columns.get_loc(year)] = mean
                else:
                    break
