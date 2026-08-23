import os
import sys
import ctypes

def get_short_path(path: str) -> str:
    if os.name == 'nt':
        buf = ctypes.create_unicode_buffer(500)
        ctypes.windll.kernel32.GetShortPathNameW(path, buf, 500)
        return buf.value if buf.value else path
    return path

short_python = get_short_path(sys.executable)
os.environ["PYSPARK_PYTHON"] = short_python
os.environ["PYSPARK_DRIVER_PYTHON"] = short_python

print(f"Short Python path: {short_python}")

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Test") \
    .master("local[1]") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .config("spark.ui.enabled", "false") \
    .getOrCreate()

print("Spark initialized successfully!")
df = spark.createDataFrame([(1, "A"), (2, "B")], ["id", "val"])
df.show()
spark.stop()
