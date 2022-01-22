import os
import data_plotter

companies = []  # 一个队列，存储公司的名字
plotters = {}   # 一个字典，存储公司的预测模型
start_year = 2011 # 训练数据开始年份
end_year = 2020 # 训练数据结束年份
pred_year = 2021 # 预测年份

def make_summary(company_name):
    print('\nPrediction Started: ' + company_name)
    plotter = plotters[company_name]  # 将公司名构造成一个字典
    plotter.show_whole_time_series()
    plotter.show_time_series(start_year=start_year, end_year=end_year)
    plotter.show_preprocessed_prices(start_year=start_year, end_year=end_year)
    plotter.show_gp_prediction(train_start=start_year, train_end=end_year, pred_year=pred_year)
    # plotter.show_time_series(start_year=start_year, end_year=end_year)
    # plotter.show_gp_prediction(train_start=start_year, train_end=2020, pred_year=2021, pred_quarters=[3,4])
    print('\nPrediction Done: ' + company_name)


def __init_data():
    if not os.path.isdir("./Results/"): # 创建存储结果的目录
            os.mkdir("./Results/")
    for company in os.listdir('./Data/'):  # 遍历Data文件下的所有文件名(这里就是公司名称)
        current_company = company.split('.')[0]  # 去除".csv"后缀
        # print(current_company)
        if not os.path.isdir("./Results/"+current_company):
            os.mkdir("./Results/"+current_company)
        companies.append(current_company)  # 加入新公司
        plotters[current_company] = data_plotter.Plotter(company_name=current_company) 

def main():
    __init_data()
    for company in companies:
        make_summary(company)
    print("\nAll Predictions Done!")

if __name__ == "__main__":
    main()
