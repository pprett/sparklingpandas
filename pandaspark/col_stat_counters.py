"""
This module provides statistics for L{PRDD}s.
Look at the stats() method on PRDD for more info.
"""
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from pandaspark.utils import add_pyspark_path, run_tests
import scipy.stats as scistats
add_pyspark_path()

from pyspark.statcounter import StatCounter

class ColumnStatCounters(object):
    """
    A wrapper around StatCounter which collects stats for multiple columns
    """

    def __init__(self, dataframes = [], columns = []):
        """
        Creates a stats counter for the provided data frames
        computing the stats for all of the columns in columns.
        Parameters
        ----------
        dataframes: list of dataframes, containing the values to compute stats on
        columns: list of strs, list of columns to compute the stats on
        """
        self._column_stats = {column_name: StatCounter() for column_name in columns}
 
        for df in dataframes:
            self.merge(df)


    def merge(self, frame):
        """
        Add another DataFrame to the accumulated stats for each column.
        Parameters
        ----------
        frame: pandas DataFrame we will update our stats counter with.
        """
        for column_name, counter in self._column_stats.items():
            count, min_max_tup, mean, unbiased_var, skew, kurt = scistats.describe(frame[[column_name]].values)
            stats_counter = StatCounter()
            stats_counter.n = count
            stats_counter.mu = mean
            stats_counter.m2 = (count - 1) * unbiased_var # only save the numerator of unbiased var
            stats_counter.minValue, stats_counter.maxValue = min_max_tup
            self._column_stats[column_name] = self._column_stats[column_name].mergeStats(stats_counter)
        return self

    def merge_stats(self, other_col_counters):
        """
        Merge statistics from a different column stats counter in to this one.
        Parameters
        ----------
        other_column_counters: Other col_stat_counter to marge in to this one.
        """
        for column_name, counter in self._column_stats.items():
            print "XXXXXXXX Merging column stats where std1 is {0} and std2 is {1}".format(self._column_stats[column_name].stdev(),
                                                                other_col_counters._column_stats[column_name].stdev())
            #TODO(juliet): ensure that merging stats counters holding info for only one var correctly agg.
            self._column_stats[column_name] = self._column_stats[column_name]\
                    .mergeStats(other_col_counters._column_stats[column_name])
        return self


    def __str__(self):
        str = ""
        for column, counter in self._column_stats.items():
            str += "(field: %s,  counters: %s)" % (column, counter)
        return str

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    run_tests()
