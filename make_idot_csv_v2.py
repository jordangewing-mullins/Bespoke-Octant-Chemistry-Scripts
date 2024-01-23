"""
This script converts a standard echo transfer sheet into an IDOT transfer sheet
"""
import pandas, xlwt
from xlwt import Workbook

all_factors_filename = " "
infile_name = 'Plate3.csv' # set the name of your OG csv transfer sheet here
all_factors_df = pandas.read_csv(infile_name, index_col=False)

print(df.head())

library_type = input('What kind of library is this? (full, pilot, custom)\n')

# function to get unique values
def unique(list1):
    unique_list = []
    for x in list1:
        if x not in unique_list:
            unique_list.append(x)
    return unique_list

unique_reagents = unique(df['Source Well'])  # this lists all the unique reagents

# for the IDOT we assume a dead volume of 8 uL (it's actually 5, but I like to do extra)
dead_vol = 8*1000 # 8 uL
max_vol = 80*1000  # 80 uL
amt_liquid_available = max_vol - dead_vol # working volume

#fill A1, then B1, down the column, then move to the next column
source_plate_rows = ['A','B','C','D','E','F','G','H']
source_plate_cols = [str(x+1) for x in range(12)]
order_of_source_plate_filling = []
for i in source_plate_cols:
    for j in source_plate_rows:
        order_of_source_plate_filling.append(j+i)

wb = Workbook() # Workbook is created
sheet1 = wb.add_sheet('Sheet 1')
sheet1.write(3, 0, 'Source Well')
sheet1.write(3, 1, 'Target Well')
sheet1.write(3, 2, 'Volume [uL]')
sheet1.write(3, 3, 'Liquid Name')
sheet1.write(0, 0, '96Template')
sheet1.write(1, 0, 'S.100 Plate')
sheet1.write(1, 1, 'Source Plate 1')
sheet1.write(1, 3, '0.00008')
sheet1.write(1, 4, 'MWP 1536')
sheet1.write(1, 5, 'Target Plate 1')
sheet1.write(1, 7, 'Waste Tube')
sheet1.write(2, 0, 'DispenseToWaste=True')
sheet1.write(2, 1, 'DispenseToWasteCycles=3')
sheet1.write(2, 2, 'DispenseToWasteVolume=1e-7')
sheet1.write(2, 3, 'UseDeionisation=True')
sheet1.write(2, 4, 'OptimizationLevel=ReorderAndParallel')
sheet1.write(2, 5, 'WasteErrorHandlingLevel=Ask')
sheet1.write(2, 6, 'SaveLiquids=Ask')
sheet1.write(0, 1, '1.7.2021.1105')
sheet1.write(0, 2, '<User Name>')
sheet1.write(0, 3, '5/9/2022')
sheet1.write(0, 4, '1:08:00 PM')
row_for_excel = 4

US_1536_plate_rows = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB','AC','AD','AE','AF']
US_1536_plate_columns = list(range(1,49))
list_of_1536_wells_US = []
for x in US_1536_plate_rows:
    for i in range(1,49):
        well = x+str(i)
        list_of_1536_wells_US.append(well)

GERMAN_1536_plate_rows = ['Aa','Ab','Ac','Ad','Ba','Bb','Bc','Bd','Ca','Cb','Cc','Cd','Da','Db','Dc','Dd','Ea','Eb','Ec','Ed','Fa','Fb','Fc','Fd','Ga','Gb','Gc','Gd','Ha','Hb','Hc','Hd']
list_of_1536_wells_German = []
for x in GERMAN_1536_plate_rows:
    for i in range(1,49):
        well = x+str(i)
        list_of_1536_wells_German.append(well)



US_to_Geman_convention = {list_of_1536_wells_US[i]: list_of_1536_wells_German[i] for i in range(len(list_of_1536_wells_US))} # dictionary where keys are US wells and values are cognate German wells
print(df['Destination Well'])
df['Destination Well'] = [US_to_Geman_convention[x] for x in df['Destination Well']]  # convert detination wells to german convention

# this variable isn't that clear. Go back and fix this.
source_well_index = -1 # if you want the transfer to start at B1, for example, you would add 8 to this value 
for reagent in unique_reagents:
    df_truncated = df.copy()
    df_truncated = df_truncated[df_truncated['Source Well'] == reagent] #make a truncated dataframe for each reagent
    print(df_truncated)
    for i in range(len(df_truncated)):
        volume = df_truncated['Transfer Volume'].iloc[i]
        dest_well = df_truncated['Destination Well'].iloc[i] 
        volume_left = amt_liquid_available - volume
        if volume_left < 0 or i == 0: #if we run out of volume or if we move onto a new liquid change source wells
            source_well_index += 1
        source_well = order_of_source_plate_filling[source_well_index] 
        sheet1.write(row_for_excel, 0, source_well)
        sheet1.write(row_for_excel, 1, dest_well)
        sheet1.write(row_for_excel, 2, str(volume/1000))
        sheet1.write(row_for_excel, 3, reagent)
        row_for_excel += 1 # move to the next row

# save new file
outfile_name = infile_name.split('.')[0]+'_IDOT.xls'
wb.save(outfile_name)

# convert xls to csv
df_for_csv = pandas.DataFrame(pandas.read_excel(outfile_name))
csv_name = outfile_name.split('.')[0]+'.csv'
df_for_csv.to_csv(csv_name, index=False)
