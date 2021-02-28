import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 10)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("/Users/hikmetselimtalu/Desktop/Dersler/week_3/online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")
df = df_.copy()

df.info()
df.isnull().sum()
df.dropna(inplace=True)
df.shape
df.head()
# İade edilen ürünler listeden çıkarıldı.
df = df[~df["Invoice"].str.contains("C", na=False)]
df['TotalPrice'] = df['Quantity'] * df['Price']

# Veri setindeki bazı betimsel istatistikler

# 1. Eşsiz fatura sayıları
df['Invoice'].nunique()

# 2. Grup bazında ülkelere göre toplam satış fiyatları
df.groupby('Country').agg({'TotalPrice': 'sum'})

# 3. En çok tecih edilen ürünlerin listesi
df.groupby('Description').agg({'Quantity': 'sum'}).sort_values('Quantity', ascending=False)

# 4. Hangi üründen kaçar tane var?
df["Description"].value_counts().head()

# 5. En pahalı ürünler listesi
df.sort_values('Price', ascending=False).head()

# 6. Hangi ülkeden kaçar tane sipariş geldi?
df['Country'].value_counts()


##############################
# Calculating RFM Metrics
##############################
# 1 Recency Değeri
# 2 Frequency Değeri
# 3 Monetary Değeri
df.head()
df['InvoiceDate'].max()

today_date = dt.datetime(2011, 12, 11)
# Hesaplama hatası yaşamamak adına 2 eklendi

rfm =df.groupby('Customer ID').agg({'InvoiceDate': lambda date: (today_date - date.max()).days,
                           'Invoice': lambda num: len(num),
                           'TotalPrice': lambda total: total.sum()})


rfm.head()
rfm.columns = ['Recency', 'Frequency', 'Monetary']

rfm[~(rfm['Frequency'] > 0) & (rfm['Monetary'] > 0)]
# Bir anormallik yok

##############################
# Calculating RFM Scores
##############################


rfm['RecencyScores'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm['FrequencyScores'] = pd.qcut(rfm['Frequency'], 5, labels=[1, 2, 3, 4, 5])
rfm['MonetaryScores'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm['RFM_Score'] = (rfm['RecencyScores'].astype(str) +
                    rfm['FrequencyScores'].astype(str) +
                    rfm['MonetaryScores'].astype(str))

#########################################
# Naming & Analysing RFM Segments
#########################################
# replace fonksiyonunun içinde regex argumanı için ön tanımlı seg_map sözlüğü

seg_map = {
    r'[1-2][1-2]': 'Hibernating',
    r'[1-2][3-4]': 'At_Risk',
    r'[1-2]5': 'Cant_Loose',
    r'3[1-2]': 'About_to_Sleep',
    r'33': 'Need_Attention',
    r'[3-4][4-5]': 'Loyal_Customers',
    r'41': 'Promising',
    r'51': 'New_Customers',
    r'[4-5][2-3]': 'Potential_Loyalists',
    r'5[4-5]': 'Champions'
}

rfm['Segment'] = rfm['RecencyScores'].astype(str) + rfm['FrequencyScores'].astype(str)
rfm['Segment'] = rfm['Segment'].replace(seg_map, regex=True)

customer_segment = rfm[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg(["mean"])
customer_segment['Segment_Count'] = rfm['Segment'].value_counts()
customer_segment = customer_segment.sort_values('Segment_Count', ascending=True)


customer_segment.columns = [i[0] if i[1] == '' else i[0] + '_' + i[1] for i in customer_segment.columns]
customer_segment.columns = ["Recency_M", "Frequency_M", "Monetary_M", 'Count']
customer_segment.sort_values('Frequency_M')


# new_score
# Pozitifleri etkili değerleri çarpar,
# negatifleri etkili değerleri bölersek
# ve çıkan değerleri sort edersek en optimum kazanç sağlayan veriyi elde ederiz.

customer_segment['new_score'] = ((customer_segment['Frequency_M'] * customer_segment['Monetary_M'] *
                                 customer_segment['Count']) / customer_segment['Recency_M'])

customer_segment.sort_values('new_score', ascending=False)

# Buna göre kampanya yapılacak 3 segment:
# 1- Champions
# 2- Loyal_Customers
# 3- Potential_Loyalists

rfm[rfm['Segment'] == 'Loyal_Customers'].index

new_df = pd.DataFrame()
new_df['Loyal_Customers'] = rfm[rfm['Segment'] == 'Loyal_Customers'].index
new_df.to_csv('Loyal_Customers.csv')