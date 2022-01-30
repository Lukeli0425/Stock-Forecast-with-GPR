# Stock Forecast with GPR
## THUEE 随机过程 Project

This is my implemention of the course project for **_Stochastic Processes_**. I built an algorithm using Guassian Process Regression that preditcs the stock prices based on previous observations. The project is implemented with Python and [Scikit Learn](https://scikit-learn.org/stable/modules/classes.html?highlight=sklearn.gaussian_process#module-sklearn.gaussian_process).

<div align=center><img src="./Results_63SE+17ESS/SBUX_2021_prediction.png" width=800><img/></div>

### 文件清单
	./Data/				存放股票数据
	./Results/			预测结果曲线（代码自动生成）
	./Results_SE/			只使用SE协方差函数的预测结果
	./Results_ESS/			只使用ESS协方差函数的预测结果
	./Results_63SE+17ESS/		使用SE和ESS组合的协方差函数的预测结果
	./References			参考文献
	gpr.yaml			虚拟环境文件
	predict.py			预测主程序
	data_plotter.py		      	封装绘图给你
	gpr_wrapper.py			封装GPR模型
	data_handler.py			封装读入数据功能

### 代码运行说明

1. 创建虚拟环境

代码主要依赖包括：numpy、pandas、sklearn和matplotlib，下载这四个包即可运行代码。也可根据环境文件gpr.yaml来配置环境。

2. 数据格式

直接从[Nasdaq](http://www.nasdaq.com/)下载的csv文件可以直接使用。或者将csv文件第一列命名为”Date”，记录交易日期，第5列命名为”Close”记录对应价格，例如下图所示：

3. 运行代码

将股票数据csv文件放到./Data文件夹下，运行predict.py后即可在/Results文件夹查看预测结果。

### 参考资料
[1] M.Ebden, " Gaussian Processes for Regression An Quick Introduction”

[2] M.T. Farrell, et al, “Gaussian Process Regression Models for Predicting Stock Trends”. 

[3] Long-term Stock Market Forecasting using Gaussian Processes

[4] [scikit-learn.gaussian_process官方文档](https://scikit-learn.org/stable/modules/gaussian_process.html?highlight=gpr#radial-basis-function-rbf-kernel)

[5] https://github.com/gdroguski/GaussianProcesses/
