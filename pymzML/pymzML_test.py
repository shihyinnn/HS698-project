import sys
import pymzml
# import get_example_file
# import operator.item
import collections
from collections import defaultdict as ddict
from operator import itemgetter
# import extractIonChromatogram

# Example
"""
# 1. Finding a peak (good)
example_file = get_example_file.open_example('deconvolution.mzML.gz')
run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
for spectrum in run:
    if spectrum["ms level"] == 2:
            peak_to_find = spectrum.hasPeak(1016.5404)
            print(peak_to_find)
"""
"""
# 2. Plotting a spectrum (good)
mzMLFile = 'profile-mass-spectrum.mzml'
get_example_file.open_example(mzMLFile)
run = pymzml.run.Reader("mzML_example_files/"+mzMLFile, MSn_Precision = 25e-6)
p = pymzml.plot.Factory()
for spec in run:
    p.newPlot()
    p.add(spec.peaks, color=(200,00,00), style='circles')
    p.add(spec.centroidedPeaks, color=(00,00,00), style='sticks')
    p.add(spec.reprofiledPeaks, color=(00,255,00), style='circles')
    p.save( filename="output/plotAspect.xhtml", mzRange = [744.7,747] )


# 2.1 Try to plot other mzML data
run = pymzml.run.Reader("/Users/jenniferchen/github/HS698/samples/peakpicker_tutorial_1.mzML", MSn_Precision = 25e-6)
p = pymzml.plot.Factory()
for spec in run:
    p.newPlot()
    p.add(spec.peaks, color=(200,00,00), style='circles')
    p.add(spec.centroidedPeaks, color=(00,00,00), style='sticks')
    p.add(spec.reprofiledPeaks, color=(00,255,00), style='circles')
    p.save( filename="output/peakpicker_tutorial_1.xhtml" )
"""
"""
# 3. Abundant precursor
example_file = get_example_file.open_example('deconvolution.mzML.gz')
run = pymzml.run.Reader(example_file , MS1_Precision = 5e-6 , MSn_Precision = 20e-6 )
precursor_count_dict = ddict(int)
for spectrum in run:
    if spectrum["ms level"] == 2:
        if "precursors" in spectrum.keys():
            precursor_count_dict[round(float(spectrum["precursors"][0]["mz"]),3)] += 1
for precursor, frequency in sorted(precursor_count_dict.items()):
    print("{0}\t{1}".format(precursor, frequency))
"""
"""
# 4. Compare Spectra (good)
spec1 = pymzml.spec.Spectrum(measuredPrecision = 20e-5)
spec2 = pymzml.spec.Spectrum(measuredPrecision = 20e-5)
spec1.peaks = [ ( 1500,1 ), ( 1502,2.0 ), (1300,1 )]
spec2.peaks = [ ( 1500,1 ), ( 1502,1.3 ), (1400,2 )]
print spec1.similarityTo( spec2 )
print spec1.similarityTo( spec1 )
"""
"""
# 5. Query Obo files

"""

"""
# 6. Highest peaks (good)
# example_file = get_example_file.open_example('deconvolution.mzML.gz')
run = pymzml.run.Reader('/Users/jenniferchen/github/HS698/Flask_app/uploads/peakpicker_tutorial_1.mzML', MS1_Precision = 5e-6, MSn_Precision = 20e-6)
# run = pymzml.run.Reader(example_file, MS1_Precision = 5e-6, MSn_Precision = 20e-6)
for spectrum in run:
    if spectrum["ms level"] == 2:
        if spectrum["id"] == 1770:
            for mz, i in spectrum.highestPeaks(5):
                print(mz, i)
"""

# 7. extract a specific Ion Chromatogram (EIC, XIC) (corrected)
MASS_2_FOLLOW = 810.53
# example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
# run = pymzml.run.Reader(example_file, MS1_Precision = 20e-6, MSn_Precision = 20e-6)

run = pymzml.run.Reader('/Users/jenniferchen/untitled folder/example_scripts/mzML_example_files/small.pwiz.1.1.mzML', MS1_Precision = 20e-6, MSn_Precision = 20e-6)
timeDependentIntensities = []
for spectrum in run:
    if spectrum['ms level'] == 1:
        matchList = spectrum.hasPeak(MASS_2_FOLLOW)
        if matchList != []:
            for mz, I in matchList:
                timeDependentIntensities.append( [ spectrum['scan start time'], I, mz ])
print timeDependentIntensities
# lst = []
for rt, i, mz in timeDependentIntensities:
#     # lst.append(rt)
    print('{0:5.3f} {1:13.4f}       {2:10}'.format( rt, i, mz ))


"""
# 8. Accessing the original XML Tree of a spectrum (good)
example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
run = pymzml.run.Reader(example_file, MSn_Precision=250e-6)
spectrum = run[1]
for element in spectrum.xmlTree:
    print('-' * 40)
    print(element)
    print(element.get('accession'))
    print(element.tag)
    print(element.items())
"""

"""
# 9. Write mzML
example_file = get_example_file.open_example('small.pwiz.1.1.mzML')
run  = pymzml.run.Reader(example_file, MS1_Precision = 5e-6)
run2 = pymzml.run.Writer(filename = 'write_test.mzML', run= run , overwrite = True)
specOfIntrest = run[2]
run2.addSpec(specOfIntrest)
run2.save()

"""






"""
mzMLFile = 'profile-mass-spectrum.mzml'
get_example_file.open_example(mzMLFile)
run = pymzml.run.Reader("mzML_example_files/"+mzMLFile, MSn_Precision = 25e-6)
p = pymzml.plot.Factory()
for spec in run:
    p.newPlot()
    p.add(spec.peaks, color=(200,0,0), style='circles')
    p.add(spec.centroidedPeaks, color=(0,0,0), style='sticks')
    p.add(spec.reprofiledPeaks, color=(0,255,0), style='circles')
    p.save( filename="output/plotAspect.xhtml" , mzRange = [744.7,747] )

msrun = pymzml.run.Reader("/Users/jenniferchen/github/HS698/samples/peakpicker_tutorial_1.mzML")
for spectrum in msrun:
    # print spectrum
    # print spectrum['ms level']
    if spectrum['ms level'] == 1:
        peak_to_find = spectrum.haspeak(1016.5404)
        print peak_to_find
        # print spectrum

# spectrum_with_nativeID_100 = msrun[100]
# print spectrum_with_nativeID_100
"""