"""
PySpark SparkSession Factory Module.
Configures local standalone SparkSession for Data Lake Medallion operations.
"""

import os
import sys
import ctypes

def get_short_path(path: str) -> str:
    if os.name == 'nt':
        try:
            buf = ctypes.create_unicode_buffer(500)
            ctypes.windll.kernel32.GetShortPathNameW(path, buf, 500)
            if buf.value:
                return buf.value
        except Exception:
            pass
    return path

# Ensure PySpark workers use valid Python executable path without space issues
short_python = get_short_path(sys.executable)
os.environ["PYSPARK_PYTHON"] = short_python
os.environ["PYSPARK_DRIVER_PYTHON"] = short_python

# Set HADOOP_HOME & dummy winutils for Windows standalone PySpark file writing
hadoop_dir = os.path.abspath(os.path.join(os.getcwd(), "data", "hadoop"))
bin_dir = os.path.join(hadoop_dir, "bin")
os.makedirs(bin_dir, exist_ok=True)
os.environ["HADOOP_HOME"] = hadoop_dir

winutils_exe = os.path.join(bin_dir, "winutils.exe")
if not os.path.exists(winutils_exe):
    try:
        with open(winutils_exe, "wb") as f:
            f.write(b"")
    except Exception:
        pass

from pyspark.sql import SparkSession

def get_spark_session(app_name: str = "EnterpriseDataPlatform-Spark") -> SparkSession:
    """Initializes and returns an optimized PySpark SparkSession instance."""
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.ui.enabled", "false")
    )
    
    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

if __name__ == "__main__":
    spark = get_spark_session("SparkFactoryTest")
    print(f"Spark Version: {spark.version}")
    print(f"Master: {spark.sparkContext.master}")
    df = spark.createDataFrame([(1, "Banking"), (2, "Credit Card")], ["id", "domain"])
    df.show()
    spark.stop()
