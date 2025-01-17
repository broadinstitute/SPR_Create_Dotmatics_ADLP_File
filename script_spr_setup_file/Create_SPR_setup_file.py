import pandas as pd
from datetime import datetime
import os
import platform
import argparse
import numpy as np
from _version import __version__

# Get the users Home Directory
if platform.system() == "Windows":
    from pathlib import Path
    homedir = str(Path.home())
else:
    homedir = os.environ['HOME']

# Use argparse to parse the arguments instead of click.
parser = argparse.ArgumentParser(description='Script for Creating an SPR setup file.')
parser.add_argument("-c", "--clip", help="Option to indicate setup table contents are on the clipboard.",
                    action='store_true',
                    default=False)


def spr_setup_sheet(args=None):
    """
    Creates the setup file necessary to run a dose response protocol on a Biacore instrument.
    :param clip: Optional flag to indicate that the contents of the setup file are on the clipboard.
    """

    # Extract the command line arguments
    args = parser.parse_args(args=args)

    # Determine at runtime if the user wants to format the file for a Biacore 8k run.
    process_for_8k = False

    # Ask user if they want the output table to be formatted for the 8K
    while True:
        process_for_8k_confirm = input("Do you want to format the file for Biacore 8K [y/N]?")

        if (process_for_8k_confirm == 'y') | (process_for_8k_confirm == 'Y'):
            process_for_8k = True
            print('Process for 8K:', process_for_8k)

        if ((process_for_8k_confirm == 'y') |
            (process_for_8k_confirm == 'Y') |
            (process_for_8k_confirm == 'n') |
            (process_for_8k_confirm == 'N')):
            break
    
    try:
        if args.clip:
            df_setup_ori = pd.read_clipboard()
        else:
            file = input('Paste the path to the setup table: ')
            df_setup_ori = pd.read_csv(file)
    except:
        raise ImportError("Issues reading contents of file.")

    # If process_for_8k is True, preform checks of the current supported scenarios.
    if process_for_8k:
        if not len(df_setup_ori) % 8 == 0:
            print("This script currently only supports runs using all 8 needles.\n")
            print("Exiting program... Please try again.")
            raise RuntimeError

    # Reformat the original table for the Biacore instruments. (S200, T200, 8K)
    try:
        # If plate barcode column doesn't exist, add it.
        plate_bar = True
        if 'Plate_Barcode' not in df_setup_ori.columns:
            df_setup_ori.loc[:, 'Plate_Barcode'] = ''
            plate_bar = False

        # Trim the sheet down to only the columns we need for the SPR setup sheet.
        df_setup_trim = df_setup_ori.loc[:, ['Broad ID', 'MW', 'Plate_Barcode', 'Barcode', 'Test [Cpd] uM',
                                             'fold_dil', 'num_pts']]

        # Start building the setup sheet.
        # Store the dimensions of the DataFrame in variables that are used later in the method.
        nRows, nCols = df_setup_trim.shape

        # Create empty list used to build up the final DataFrame.
        brd_list = []
        mw_list = []
        bar_list = []
        conc_list = []
        bar_plate_list = []

        # Inner method uses the original DataFrame to construct each column of the setup sheet.
        def create_lists(header, list):

            if header == 'Broad ID':
                unique_brd = 1
                for cmpd in range(nRows):
                    value = df_setup_trim.iloc[cmpd][header]

                    for i in range(int(df_setup_trim.iloc[cmpd]['num_pts']) + 2):

                        # As the SPR field limit is only 15 characters trim the BRD's
                        if len(value) == 22:
                            v = value[:3] + '-' + value[9:13] + '_' + str(unique_brd)
                            list.append(v)
                        else:
                            v = value + '_' + str(unique_brd)
                            list.append(v)
                    unique_brd += 1
            else:
                for cmpd in range(nRows):
                    value = df_setup_trim.iloc[cmpd][header]
                    for i in range(int(df_setup_trim.iloc[cmpd]['num_pts']) + 2):
                        list.append(value)

        # Inner method needed to create the dose response column.
        def dose_conc_list():

            for cmpd in range(nRows):

                # empty list to store each concentration in the dose response
                dose_list = []

                # Include two blank injections for each compound
                dose_list.append(0)
                dose_list.append(0)

                top = df_setup_trim.iloc[cmpd]['Test [Cpd] uM']  # store top dose in a variable.

                for i in range(int(df_setup_trim.iloc[cmpd]['num_pts'])):
                    dose_list.append(top)
                    top = top / float(
                        df_setup_ori.iloc[cmpd]['fold_dil'])  # use value in original DataFrame to determine
                    # the fold of dilution.
                dose_list.sort(reverse=False)

                # Want one final concentration list.  So add each concentration in the dose_list to the final conc_list.
                for c in dose_list:
                    conc_list.append(c)

        # Create the columns in the setup sheet
        create_lists(header='Broad ID', list=brd_list)
        create_lists(header='MW', list=mw_list)
        dose_conc_list()
        create_lists(header='Barcode', list=bar_list)

        if plate_bar:
            create_lists(header='Plate_Barcode', list=bar_plate_list)

        # Create the final DataFrame from all of the lists.
        if plate_bar:
            final_df = pd.DataFrame({'BRD': brd_list, 'MW': mw_list, 'CONC': conc_list,
                                 'BAR': bar_list, 'PLATE_BAR': bar_plate_list})
        else:
            final_df = pd.DataFrame({'BRD': brd_list, 'MW': mw_list, 'CONC': conc_list,
                                     'BAR': bar_list})

        # Reorder the columns
        if plate_bar:
            final_df = final_df.loc[:, ['BRD', 'MW', 'CONC', 'BAR', 'PLATE_BAR']]
        else:
            final_df = final_df.loc[:, ['BRD', 'MW', 'CONC', 'BAR']]

        if process_for_8k:
            final_df = process_df_for_8k(df_setup_ori=df_setup_ori, final_df=final_df)

            # Save the file to the desktop
            save_output_file(df_final=final_df)
        else:
            # Save the file to the desktop
            save_output_file(df_final=final_df)

        return final_df

    except Exception:
        raise RuntimeError('Something is wrong. Please check.')


def process_df_for_8k(df_setup_ori, final_df):
    """
    Method that formats the setup file for the Biacore 8k Instrument

    Complication: No easy way to sort the final_df for the 8k.
    Must treat the zeros or blank injections differently as there are 2 blanks for every compound titration.
    In addition, the 8k head sweeps across an entire 384 well plate so there will be more than one compound
    titration for each of the 8 needles in a single pass of the 8 needled head and therefore more than
    one set of blanks separated with compound titrations within the plate.

    Logic
    1. From the final_df created for non-8k instruments above...
    2. Locate and label the first and second blank injections (zeros).
    3. Sort the blank injections
    4. Remove the non-blank injections and save to a separate df.
    5. Separate the sorted blank injections into df's of 8 rows each that correspond to the 8 needles of the 8k.
    6. Add each 8 rowed df to a new list.
    7. Reorder the list of df's so that they are consistent with the correct order across the plate from left to right.
    8. Address the non-zero points by taking the original final_df above and removing the zero points.
    9. Separate each group of titrations (number of points/ curve * 8 needles) into separate dfs.
    10. Label each row of each separated df so that it can be sorted for the 8k needle.
    11. Sort each df.
    12. Concatenate the zero df and non-zero df's in the correct order into the final df.
    """

    # Variables needed to reorganize compound titrations for 8k.
    num_pts_curve = int(df_setup_ori.iloc[1]['num_pts'])
    num_active_needles = 8
    total_pts_per_pass = num_pts_curve * num_active_needles

    # add column for sorting
    final_df.loc[:, 'sort_zero'] = ''

    # Variables needed to keep track of where a zero is located in original df
    zero_num = 2
    zero_count = 1

    for i in range(zero_num):
        for index, row in final_df.iterrows():
            if row['CONC'] == 0:
                if (index % 2 == 0) & (i == 0):
                    final_df.loc[index, 'sort_zero'] = zero_count
                    zero_count += 1
                elif (index % 2 != 0) & (i != 0):
                    final_df.loc[index, 'sort_zero'] = zero_count
                    zero_count += 1
            else:
                final_df.loc[index, 'sort_zero'] = np.nan

    # Create a copy of the final df so that the final_df is preserved.
    df_zeros = final_df.copy()
    df_zeros = df_zeros.dropna(how='any', subset=['sort_zero'])

    df_zeros = df_zeros.sort_values(['sort_zero'])
    df_zeros = df_zeros.reset_index(drop=True)

    # Create a list to store the sorted DataFrames of zero concentration.
    ls_df_zeros = []

    row_start = 0
    row_end = num_active_needles

    # Group into df's of 8 rows each corresponding to the 8 needles.
    for i in range(0, int(len(df_zeros)), num_active_needles):
        df_active = df_zeros.iloc[row_start:row_end, :]
        df_active = df_active.reset_index(drop=True)
        del df_active['sort_zero']
        ls_df_zeros.append(df_active)
        row_start += 8
        row_end += 8

    # At this point the blanks ordered are placed into separate DF's of length 8 for the 8 needles of the 8k.
    # Now the non-blank concentrations must be handled...
    df_non_zero = final_df[final_df['sort_zero'].isna()].copy()
    df_non_zero.loc[:,'sort_non_zero'] = ''
    df_non_zero = df_non_zero.reset_index(drop=True)

    # As done with the blanks, split DF into groups of 8 for the 8 needles
    ls_dfs_non_zeros = []
    row_start = 0
    row_end = total_pts_per_pass

    # Create a list of DataFrames separated by each pass of the 8k head.
    for i in range(0, int(len(df_non_zero)), total_pts_per_pass):
        df_active = df_non_zero.iloc[row_start:row_end, :]
        df_active = df_active.reset_index(drop=True)
        ls_dfs_non_zeros.append(df_active)
        row_start += total_pts_per_pass
        row_end += total_pts_per_pass

    # For each df in the non zero df list..
    # Pull out the df and label the sorting column so that sorting can be done.
    ls_dfs_non_zeros_sorted = []

    for df_active in ls_dfs_non_zeros:

        non_zero_count = 1
        row_count = 0

        for i in range(0, num_pts_curve):
            for j in range(0, int(len(df_active)), num_pts_curve):
                df_active.loc[row_count, 'sort_non_zero'] = non_zero_count
                non_zero_count += 1
                row_count += num_pts_curve

            row_count = i + 1

        # Sort based on the newly created 'sort_non_zero' column
        df_active = df_active.sort_values(['sort_non_zero'])
        df_active = df_active.reset_index(drop=True)

        # Remove the columns needed for sorting
        del df_active['sort_zero']
        del df_active['sort_non_zero']

        # Append the sorted group of 8 compound titrations to the list of dfs
        ls_dfs_non_zeros_sorted.append(df_active)

    # Dict where keys are num compounds run and value is the assignment of second_zero
    # The second zero df in the list of zero df's is offset by the num cmpds run and num needles.
    keys = np.arange(8, 296, 8)
    vals = np.arange(1, 37, 1)
    sec_zero_offset_dict = dict(zip(keys, vals))

    # Create some counters
    first_zero = 0
    second_zero = sec_zero_offset_dict[len(df_setup_ori)]
    non_zero = 0

    # Calculate the number of needle passes in an experiment.
    num_needle_pass = int(len(df_setup_ori)/num_active_needles)

    # For each loop, Concat 1 needle pass of zeros and non-zero points.
    ls_df_final =[]
    for each_needle_pass in range(0, num_needle_pass):
        final_df = pd.concat([ls_df_zeros[first_zero], ls_df_zeros[second_zero],
                              ls_dfs_non_zeros_sorted[non_zero]])

        # Append the zeros and non-zeros of one needle swip to a list of df's
        ls_df_final.append(final_df)

        first_zero += 1
        second_zero += 1
        non_zero += 1

    # Concat all of the needle passes together for the final df.
    final_df = pd.concat(ls_df_final)
    final_df = final_df.reset_index(drop=True)

    return final_df


def save_output_file(df_final):
    # Truncate the year in the file name.
    now = datetime.now()
    now = now.strftime('%y%m%d_%H_%M')

    # Save file path for server Iron
    if platform.system() == "Windows":
        save_file_path_iron = os.path.join('tdts_users', 'SPR Setup Files', now + '_spr_setup_affinity_APPVersion_' +
                                           str(__version__))
    else:
        save_file_path_iron = os.path.join('/Volumes', 'tdts_users', 'SPR Setup Files',
                                       now + '_spr_setup_affinity_APPVersion_' + str(__version__))

    save_file_path_iron = save_file_path_iron.replace('.', '_')
    save_file_path_iron = save_file_path_iron + '.xlsx'

    # Backup save file path for Desktop
    save_file_path_desk = os.path.join(homedir, 'Desktop', now + '_spr_setup_affinity_APPVersion_' + str(__version__))
    save_file_path_desk = save_file_path_desk.replace('.', '_')
    save_file_path_desk = save_file_path_desk + '.xlsx'

    # Option 2 save to Desktop due to some PC's using one-drive in path.
    save_file_path_desk_opt_2 = os.path.join(homedir,'OneDrive - The Broad Institute', 'Desktop',
                                             now + '_spr_setup_affinity_APPVersion_' + str(__version__))
    save_file_path_desk_opt_2 = save_file_path_desk_opt_2.replace('.', '_')
    save_file_path_desk_opt_2 = save_file_path_desk_opt_2 + '.xlsx'

    try:
        df_final.to_excel(save_file_path_iron)
        print('Setup file has been placed on Iron in folder: SRP Setup Files')

    except:
        print('Issue connecting to Iron. Mount drive and try again.')
        print('Attempting to save file to desktop...')
        print('')

        try:
            df_final.to_excel(save_file_path_desk)
        except:
            df_final.to_excel(save_file_path_desk_opt_2)
        finally:
            print('File created on desktop.')


if __name__ == '__main__':

    spr_setup_sheet(args=None)