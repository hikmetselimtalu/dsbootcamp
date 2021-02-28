import pandas as pd
import numpy as np
import seaborn as sns
import statsmodels.stats.api as sms
from scipy.stats import shapiro
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
from statsmodels.stats.proportion import proportions_ztest
from scipy import stats
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 20)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

#######################################
##### AB Testing Ödev #####
#######################################

df_control = pd.read_excel('/Users/hikmetselimtalu/Desktop/Dersler/week_5/ab_testing_data.xlsx',
                           sheet_name='Control Group')

df_test = pd.read_excel('/Users/hikmetselimtalu/Desktop/Dersler/week_5/ab_testing_data.xlsx',
                        sheet_name='Test Group')

df_control.isna().any()
df_test.isna().any()
df_test.shape
df_control.shape
df_control.head()

df_control.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T

sns.set_theme(style="whitegrid")


def draw_plot(dataframe):
    for i in dataframe.columns:
        sns.boxplot(x=dataframe[i])
        plt.show()


draw_plot(df_control)
draw_plot(df_test)

# Test grubunda aykırı gözlemler mevcut.


def outlier_thresholds(dataframe, variable):
    quartile1 = dataframe[variable].quantile(0.25)
    quartile3 = dataframe[variable].quantile(0.75)
    interquantile_range = quartile3 - quartile1
    up_limit = quartile3 + 1.5 * interquantile_range
    low_limit = quartile1 - 1.5 * interquantile_range
    return low_limit, up_limit


def replace_with_thresholds(dataframe, variable):
    low_limit, up_limit = outlier_thresholds(dataframe, variable)
    dataframe.loc[(dataframe[variable] < low_limit), variable] = low_limit
    #dataframe.loc[(dataframe[variable] > up_limit), variable] = up_limit


replace_with_thresholds(df_test, 'Impression')

draw_plot(df_test) # Aykırı değerler düzeltildi.


def check_2_frame(dataframe_1, value, dataframe_2):
    mean_c = dataframe_1[value].mean()
    median_c = dataframe_1[value].median()
    std_c = dataframe_1[value].std()
    mean_t = dataframe_2[value].mean()
    median_t = dataframe_2[value].median()
    std_t = dataframe_2[value].std()
    print('mean_c = %.5f, median_c = %.5f, std_c = %.5f' % (mean_c, median_c, std_c))
    print('mean_t = %.5f, median_t = %.5f, std_t = %.5f' % (mean_t, median_t, std_t))

#######################################
# İki bağımsız örneklem oran testi
#######################################

df_control['Impression'].sum()
df_test['Impression'].sum()
gozlem_sayisi = np.array([df_test['Impression'].sum(), df_control['Impression'].sum()])

df_control['Click'].sum()
df_test['Click'].sum()
basari_sayisi = np.array([df_test['Click'].sum(), df_control['Click'].sum()])

df_control['Click'].sum() / df_control['Impression'].sum()
df_test['Click'].sum() / df_test['Impression'].sum()

# Matematiksel olarak bakıldığında control grubunun click/imp oranı test grubunun click/imp oranından fazla
# Peki istatistiki olarak da aralarında anlamlı bir fark var mı?
# 2 bağımsız örneklem oran testi için varsayımlar n1, n2 > 30 olduğundan sağlanmaktadır.

# H0: Click/Imp ratio aralarında anlamlı bir farklılık yoktur.
# H1: Click/Imp ratio aralarında anlamlı bir farklılık vardır.

proportions_ztest(count=basari_sayisi, nobs=gozlem_sayisi)
print('test istatistiği = %.5f, p-value = %.5f' % (proportions_ztest(basari_sayisi, gozlem_sayisi)[0],
                                                   proportions_ztest(basari_sayisi, gozlem_sayisi)[1]))

# Yorum:
# H0 hipotezi reddedilebilir iki örneklemin Click/Imp ratio'ları arasında anlamlı bir farklılık vardır. Diyebiliriz.


##############################################################################
# İki bağımsız örneklem t testi --> Purchase
##############################################################################

check_2_frame(df_control, 'Purchase', df_test)
# Ortalamalara bakıldığında test grubu matematiksel olarak önde görünüyor. Fakat sapma miktarı control grubuna göre
# daha fazla bu da istatiksel olarak güven aralığınının genişlemesine sebep olur.
# Tahmin değerleri için tutarlılıkları azaltır. İstataiksel olarak da bu ortalama anlamlı mı bakalım.

# H0: Control grubu ile test grubu satış ortlamaları arasında anlamlı bir farklılık yoktur.
# H1: Control grubu ile test grubu satış ortlamaları arasında anlamlı bir farklılık vardır.

# Varsayımlar: Normallik ve Varyans Homojenliği
# Normallik İçin Hipotez
# H0: Normal dağılım ile df_control['Purchase'], df_test['Purchase'] verisi arasında anlamlı bir fark yoktur.
# H1: Normal dağılım ile df_control['Purchase'], df_test['Purchase'] verisi arasında anlamlı bir fark vardır.

shapiro(df_control['Purchase'])
print('test istatistiği = %.5f, p-value = %.5f' % (shapiro(df_control['Purchase'])[0],
                                                   shapiro(df_control['Purchase'])[1]))

shapiro(df_test['Purchase'])
print('test istatistiği = %.5f, p-value = %.5f' % (shapiro(df_test['Purchase'])[0],
                                                   shapiro(df_test['Purchase'])[1]))

# Yorum: H0 hipotezi reddedilemez iki veride normal dağılım gözlenir denilebilir.

# Varyans Homojenliği İçin Hipotez Testi

# H0: İki grubun varyansları arasında anlamlı bir farklılık yoktur, homojendir.
# H1: İki grubun varyansları arasında anlamlı bir farklılık vardır, homojen değildir.

stats.levene(df_control['Purchase'], df_test['Purchase'])
print('Test istatistiği = %.5f, p-value = %.5f' % (stats.levene(df_control['Purchase'], df_test['Purchase'])[0],
                                                   stats.levene(df_control['Purchase'], df_test['Purchase'])[1]))

# Yorum: H0 hipotezi reddedilemez iki verinin varyansları homojendir denilebilir.
# Bağımsız iki örneklem t test yapılabilir. Varsayımlar sağlanmaktadır.

test_istatistigi, pvalue = stats.ttest_ind(df_control['Purchase'],
                                           df_test['Purchase'],
                                           equal_var=True)

print('Test istatistiği = %.5f, p-value = %.5f' % (test_istatistigi, pvalue))
# H0: Hipotezi reddedilemez iki grubun ortalamaları arasında anlamlı bir farklılık yoktur yorumu yapılabilir.

##############################################################################
# İki bağımsız örneklem t testi --> Earning
##############################################################################


check_2_frame(df_control, 'Earning', df_test)
# Matematiksel olarak bakıldığında test grubundaki kazanç daha fazla görünüyor üstelik sapma miktarı da daha az
# İstaiksel olarak inceleyelim

# H0: İki grup arasındaki Earning değerleri ortalamaları arasında anlamlı bir farklılık yoktur.
# H1: İki grup arasındaki Earning değerleri ortalamaları arasında anlamlı bir farklılık vardır.

# Varsayımlar: Normallik, Varyans Homojenliği

# H0: Normal dağılım ile Earning verisi arasında anlamlı bir farklılık yoktur
# H1: Normal dağılım ile Earning verisi arasında anlamlı bir farklılık vardır
a = shapiro(df_control['Earning'])
print('Test istatistiği = %.5f, P-value = %.5f' % (a[0], a[1]))

a = shapiro(df_test['Earning'])
print('Test istatistiği = %.5f, P-value = %.5f' % (a[0], a[1]))

# Hipotez reddedilemez denilebilir. İki dağılım da normal dağılır.

# H0: İki grubun varyansları arasında anlamlı bir farklılık yoktur. Varyansları homojendir
# H0: İki grubun varyansları arasında anlamlı bir farklılık vardır. Varyansları homojen değildir.

a = stats.levene(df_control['Earning'], df_test['Earning'])
print('Test istatistiği = %.5f, P-value = %.5f' % (a[0], a[1]))
# H0 hipotezi reddedilemez varyansları homojendir denilebilir.

test_istatistigi, pvalue = stats.ttest_ind(df_control['Earning'], df_test['Earning'], equal_var=True)
print('Test istatistiği = %.5f, p-value = %.5f' % (test_istatistigi, pvalue))

#######################
# SONUÇ
#######################

# Control grubu (click/Impression ratio) bazında daha üstün
# Purchase baz alındığında Ortalamalar arasında anlamlı bir fark yok
# Earning baz alındığında ortalamalar arasında ciddi bir fark var test grubu farkla önde


# Görülme sayısı artmış fakat tıklanma sayısı ciddi bir şekilde azalmış
# Buna bağlı olarak satışlarda bir etkilenme yok
# Fakat kazançta ciddi bir artış sağlanmış. Satış artmadan kazanç nasıl arttı? Sistemsel bir arıza olması mümkün mü?

# Kazanç ile Satış arasında bir korelasyon var mı?
# İkisi de normal olduğundan pearson korelasyonuna bakıyorum

df_control[['Purchase', 'Earning']].corr(method='pearson')
df_test[['Purchase', 'Earning']].corr(method='pearson')

# Evet aralarında bir korelasyon yok.


df_test['Impression']