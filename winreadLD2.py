import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
import numpy as np
from osgeo import gdal
import os


class LD2ToTIFFConverter(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('LD2 to TIFF Converter')

        # 创建一个垂直布局
        layout = QVBoxLayout()

        # 创建一个按钮，用于打开文件选择对话框
        self.open_button = QPushButton('Open LD2 File', self)
        self.open_button.clicked.connect(self.open_ld2_file)
        layout.addWidget(self.open_button)

        # 创建一个中心窗口部件，并设置布局
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_ld2_file(self):
        # 打开文件选择对话框
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "Select LD2 File", "", "LD2 Files (*.ld2)", options=options)
        if file:
            dir_path = os.path.dirname(file)
            base_name = os.path.splitext(os.path.basename(file))[0]
            output_file = os.path.join(dir_path, f"{base_name}.tif")
            self.convert_ld2_to_tiff(file,output_file)

    def convert_ld2_to_tiff(self, file_path,outputfile):
        # 你的 LD2 文件处理代码
        file=file_path
        # file = r"D:\python\modis\oo.ld2"
        # file = r"D:\python\modis\ld20207.ld2"



        # 一:对ld2文件
        ld2dtype = [
            ("head", "H", 10),
            ("band", "H"),
            ("proj", "H"),
            ("col", "H"),
            ("line", "H"),
            ("resX", "f"),
            ("resY", "f"),
            ("33", "f", 3),
            ("range", "f", 4),
            ("center", "f", 3),
            ("tail", 'b', (128 - 76))
        ]

        with open(file, "rb") as f:
            header_data, = np.fromfile(f, dtype=ld2dtype, count=1)

            print(header_data)

            proj = header_data['proj']
            res = header_data['resX']
            b = header_data['band']
            w = header_data['col']
            h = header_data['line']

            band_data = np.fromfile(f, dtype='H').reshape(b, h, w)
            dim = band_data.ndim
            print(dim)
            print(band_data.shape)
            # 二： 写入tiff文件
            # 创建一个新的TIFF文件

            # output_file = "D:\python\modis\outputoo12.tif"
            output_file = outputfile
            driver = gdal.GetDriverByName('GTiff')
            datatype = gdal.GDT_UInt16
            dataset = driver.Create(output_file, int(w), int(h), int(b), datatype)
            # 设置
            # 设置TIFF文件的地理变换参数
            # 这里你需要根据你的数据和投影信息来设置这些参数
            # 例如：
            # dataset.SetGeoTransform((header_data['range'][0], header_data['resX'], 0, header_data['center'][2], 0, -header_data['resY']))

            # 设置TIFF文件的投影信息
            # 这里你需要根据你的数据和投影信息来设置
            # 例如：
            # proj_wkt = header_data['proj'].decode('utf-8')
            # dataset.SetProjection(proj_wkt)
            # 设置
            # # 获取TIFF文件的带宽
            # # band = 1
            # tiff_band = dataset.GetRasterBand(int(b))
            # # 转三维向量
            # band_data = np.asarray(band_data, dtype=np.uint32)
            band_data = np.asarray(band_data, dtype=np.float32)

            # # band_data = np.asarray(band_data)
            # # 写入数据到TIFF文件
            # tiff_band.WriteArray(band_data)
            # 遍历每个波段并写入数据
            for band_index in range(1, int(b) + 1):  # band_index 从 1 开始，因为 GDAL 的波段索引是从 1 开始的
                # 获取 TIFF 文件的波段
                tiff_band = dataset.GetRasterBand(band_index)
                print(band_index)
                # 提取对应波段的数据
                # 假设 band_data 的形状为 (band_count, height, width)
                # 我们需要提取第 band_index-1 层的数据
                band_data_for_band = band_data[band_index - 1]

                # 写入数据到 TIFF 文件的当前波段
                tiff_band.WriteArray(band_data_for_band)
            # 关闭文件
            f.close()





        # 这里可以添加代码来显示转换进度或结果

        # 通知用户转换完成
        self.statusBar().showMessage("Conversion completed!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    converter = LD2ToTIFFConverter()
    converter.show()
    sys.exit(app.exec_())