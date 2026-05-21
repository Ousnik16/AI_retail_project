from pyspark.sql import SparkSession
from pyspark.sql.functions import coalesce, col, lower, regexp_replace, trim


def normalize_text(column_name: str):
    return trim(regexp_replace(lower(col(column_name)), "[^a-z0-9 ]", ""))


def run_cleaning_job():
    spark = SparkSession.builder.appName("RetailDataCleaning").getOrCreate()

    products = spark.read.option("header", True).csv("data/sample_products.csv")
    cleaned_products = (
        products.dropDuplicates(["sku"])
        .withColumn("name", normalize_text("name"))
        .withColumn("category", trim(lower(coalesce(col("category"), col("name")))))
        .withColumn("brand", trim(coalesce(col("brand"), col("category"))))
        .fillna({"category": "unknown", "brand": "unknown", "inventory_quantity": "0", "price": "0"})
        .withColumn("price", col("price").cast("double"))
        .withColumn("inventory_quantity", col("inventory_quantity").cast("int"))
    )
    cleaned_products.write.mode("overwrite").json("data/cleaned_products")

    try:
        transactions = spark.read.option("header", True).csv("data/synthetic_retail_intelligence.csv")
        cleaned_transactions = (
            transactions.dropDuplicates()
            .fillna({"channel": "online", "quantity": "1", "unit_price": "0", "line_total": "0"})
            .withColumn("product_name", normalize_text("product_name"))
            .withColumn("category", trim(lower(coalesce(col("category"), col("product_name")))))
            .withColumn("quantity", col("quantity").cast("int"))
            .withColumn("unit_price", col("unit_price").cast("double"))
            .withColumn("line_total", col("line_total").cast("double"))
        )
        cleaned_transactions.write.mode("overwrite").json("data/cleaned_transactions")
    except Exception:
        pass

    print("Cleaned products and transaction logs written to data/cleaned_*")
    spark.stop()


if __name__ == "__main__":
    run_cleaning_job()
