RSS_demo

输入数据：

（1）原始数据
文件名：CCD1_ObsTime_600_ObsNum_30.fits  
说明：原始数据文件名不能为None；按照文件名找不到对应文件的时候，不报错，设置该文件状态为False。

（2）参考文件

平场参考文件： Flat_flux.fits
灯谱文件：HgAr_flux.fits
天光背景文件：sky_noise_With_wavelength.fits
说明：参考文件名可以为None，比如程序中的bias_file=None；文件名不为None，但是找不到对应文件的时候，不报错，设置该文件状态为False。


输出数据：

rss_demo.pkl （记录原始数据和四个参考文件的状态）
