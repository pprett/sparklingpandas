import pandas as pd
import numpy.random as nprnd
import scipy.stats as scistats
import timeit

df = pd.DataFrame(nprnd.randn(10000, 1), columns=['samples'])

timeit.timeit("df.loc['samples'].describe()")
timeit.timeit("scistats.describe(df.loc['samples'].values())")
