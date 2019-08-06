# pylint: disable=no-member
import csv
import logging
from pathlib import Path
from collections import defaultdict

import pandas as pd
import yaml

class Survey:
    def create_alias_file(self, filename_override, reset=False):
        if filename_override:
            self.alias_filename = filename_override
        else:
            self.alias_filename = '.'.join(Path(self.filename).parts) + '.alias'

        if Path(self.alias_filename).is_file() and not reset:
            logging.info(f"Alias file found at {self.alias_filename}... using that. " \
                          "To overwrite, call with kwarg `reset=True`")
            self.update_aliases()
            return
            
        # create set of things to alias
        alias_set = set()
        cols = self.data_df.columns
        if isinstance(cols, pd.MultiIndex):
            for col in cols.to_flat_index():
                alias_set.update(col)
        else:
            alias_set.update(cols)
        
        alias_set.remove('')
        
        alias_map = {k:"" for k in alias_set}
        with open(self.alias_filename, 'w') as outfile:
            yaml.dump(alias_map, outfile)
        
        self.alias2full = {k:k for k in alias_set}
        self.full2alias = {k:k for k in alias_set}
        
        logging.info(f"Alias file created at {self.alias_filename}")

    def update_aliases(self):
        with open(self.alias_filename) as infile:
            alias_dict = yaml.load(infile, Loader=yaml.FullLoader)

        # TODO: check that aliases are unique and valid

        for key, val in alias_dict.items():
            if not val:
                alias_dict[key] = key
        
        self.full2alias = alias_dict
        self.alias2full = {v: k for k, v in alias_dict.items()}        

    def create_exclude_file(self, filename_override):
        if filename_override:
            self.exclude_filename = filename_override
        else:
            self.exclude_filename = '.'.join(Path(self.filename).parts) + '.exclude'

        if Path(self.exclude_filename).is_file():
            logging.info(f"Exclude file found at {self.exclude_filename}... using that.")
            self.update_exclusions()
            return

        # initial file is empty
        Path(self.exclude_filename).touch()

    def update_exclusions(self):
        self.exclusions = {}
        with open(self.exclude_filename) as infile:
            new_exclusions = yaml.load(infile, Loader=yaml.FullLoader)
        
        # TODO: check that exclusion keys are valid columns

        for key, exclusion in new_exclusions.items():
            # de-alias any aliased exclusion keys
            if key in self.alias2full.keys():
                key = self.alias2full[key]

            # TODO: check for proper structure in exclusion file

            self.exclusions[key] = set(exclusion)
        
        exclusion_mask = pd.Series([False] * len(self.data_df.index), index=self.data_df.index)
        for col, excluded_values in self.exclusions.items():
            exclusion_mask = exclusion_mask | self.data_df[col].isin(excluded_values)
        self.exclusion_mask = exclusion_mask
        n_excluded = len(self.excluded_rows())
        if n_excluded > 0:
            logging.info(f"{n_excluded} responses dropped based on specified exclusions")
        else:
            logging.warning("Specified exclusions matched no responses.")

    def data(self, exclude=True):
        if exclude:
            return self.data_df[~self.exclusion_mask]
        else:
            return self.data_df

    def excluded_rows(self):
        return self.data_df[self.exclusion_mask]

    def aliased_df(self, exclude=True):
        return self.data(exclude=exclude).rename(columns=self.full2alias)


class SurveyMonkeySurvey(Survey):
    """A survey in the format of a SurveyMonkey CSV export (from the XLS zip) with the following settings:
    * All Responses
    * Condensed
    * Actual Answer Text
    """
    
    def load_data_from_file(self, filename):
        with open(filename) as infile:
            reader = csv.reader(infile)
            header1 = next(reader)
            header2 = next(reader)
            response_rows = [row for row in reader]

        header_labels = []
        multiselect_questions = set()

        for h1, h2 in zip(header1, header2):
            if h1:
                last_nonempty_h1 = h1
            else:
                multiselect_questions.add(last_nonempty_h1)
            header_labels.append((last_nonempty_h1, h2))
            
        self.multiselect_questions = multiselect_questions
            
        data = pd.DataFrame(response_rows)
        data.columns = pd.MultiIndex.from_tuples(header_labels)
        data['Start Date'] = pd.to_datetime(data['Start Date'])
        data['End Date'] = pd.to_datetime(data['End Date'])
        
        # create an elapsed time calculated column
        data['Elapsed'] = data['End Date'] - data['Start Date']
        self.data_df = data
        
    def __init__(self, filename, 
                 alias_filename=False,
                 reset_aliases=False,
                 exclude_filename=False, 
                 drop_empty_cols=True):
        self.filename = filename
        self.load_data_from_file(filename)
        
        # drop empty columns + alert that they're being dropped
        if drop_empty_cols:
            has_data = (self.data_df == '').astype(int).sum() != len(self.data_df)
            for idx, val in has_data.iteritems():
                if not val:
                    logging.warning(f"Column {idx} has no data, dropping...")
            self.data_df = self.data_df.loc[:, has_data]
            
        self.create_alias_file(alias_filename, reset_aliases)
        self.create_exclude_file(exclude_filename)
