import os
import sys
from flask import Flask, render_template, request, redirect, url_for, \
    send_from_directory, jsonify
from werkzeug import secure_filename
import pymzml
from wtforms import Form, IntegerField, validators, StringField, DecimalField, \
    FloatField

# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

# These is the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['mzML'])


# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def get_abs_path():
    return os.path.abspath(os.path.dirname(__file__))


@app.route('/')
def index():
    return render_template('index.html')


# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and allowed_file(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file from the temporal folder to
        # the upload folder we setup
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Redirect the user to the uploaded_file route, which
        # will basically show on the browser the uploaded file

        # return filename
        return render_template("complete.html", filename=filename)
        # return redirect(url_for('uploaded_file',
        #                         filename=filename))
    else:
        return "File uploaded is not supported..."


class PeakFindingForm(Form):
    spectrum_ms_level = IntegerField('Spectrum MS Level')
    mz_value = DecimalField('MZ Value')


# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/peak_finding/<filename>', methods=["GET", "POST"])
def peak_finding(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MS1_Precision=5e-6,
                            MSn_Precision=20e-6)
    form = PeakFindingForm(request.form)

    if request.method == 'POST' and form.validate():
        # What to do when user submits form

        spectrum_ms_level = form.spectrum_ms_level.data
        mz_value = form.mz_value.data

        lst = []
        for spectrum in run:
            if spectrum["ms level"] == spectrum_ms_level:
                peak_to_find = spectrum.hasPeak(mz_value)
                if peak_to_find:
                    lst.append(peak_to_find)
        return render_template('peak_to_find.html', form=form,
                               filename=filename, lst=lst)

    # Create the form (the first time the page loads)
    return render_template('peak_to_find.html', form=form, filename=filename)


class PlotSpectrumForm(Form):
    # mz_range_start = DecimalField('Start')
    # mz_range_end = DecimalField('End')
    mz_range_start = FloatField('Start')
    mz_range_end = FloatField('End')


@app.route('/plot_spectrum/<filename>', methods=["GET", "POST"])
def plot_spectrum(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MSn_Precision=25e-6)

    form = PlotSpectrumForm(request.form)

    if request.method == 'POST' and form.validate():

        start = form.mz_range_start.data
        end = form.mz_range_end.data

        p = pymzml.plot.Factory()
        for spec in run:
            p.newPlot()
            p.add(spec.peaks, color=(200, 00, 00), style='circles')
            p.add(spec.centroidedPeaks, color=(00, 00, 00), style='sticks')
            p.add(spec.reprofiledPeaks, color=(00, 255, 00), style='circles')
            p.save(filename="static/tmp/plotAspect.xhtml", mzRange=[start, end])
        return render_template('plotAspect.html',
                               fig=url_for('static',
                                           filename='tmp/plotAspect.xhtml'),
                               form=form, p=p)

    return render_template('plotAspect.html', form=form, filename=filename)


class HighestPeakForm(Form):
    spec_ms_level = IntegerField('Spectrum MS Level')
    id_value = IntegerField('id')
    num_of_peaks = IntegerField('Number of n-highest peaks')


@app.route('/highest_peaks/<filename>', methods=["GET", "POST"])
def highest_peaks(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MS1_Precision=5e-6,
                            MSn_Precision=20e-6)

    form = HighestPeakForm(request.form)

    if request.method == 'POST' and form.validate():

        spectrum_ms_level = form.spec_ms_level.data
        id_value = form.id_value.data
        num_of_peaks = form.num_of_peaks.data

        lst = []

        for spectrum in run:
            if spectrum["ms level"] == spectrum_ms_level:
                if spectrum["id"] == id_value:
                    for mz, i in spectrum.highestPeaks(num_of_peaks):
                        lst.append((mz, i))

        return render_template('highest_peaks.html', form=form,
                               filename=filename, lst=lst)
    return render_template('highest_peaks.html', form=form, filename=filename)


class IonChromatogramForm(Form):
    mz2find = DecimalField('mz value which should be found')
    spectrum_ms_level = IntegerField('Spectrum MS Level')


@app.route('/extract_Ion_Chromatogram/<filename>', methods=["GET", "POST"])
def extract_Ion_Chromatogram(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MS1_Precision=20e-6, MSn_Precision=20e-6)
    timeDependentIntensities = []

    form = IonChromatogramForm(request.form)

    if request.method == 'POST' and form.validate():

        mz2find = form.mz2find.data  # 810.53
        spectrum_ms_level = form.spectrum_ms_level.data  # 1

        for spectrum in run:
            if spectrum['ms level'] == spectrum_ms_level:
                matchList = spectrum.hasPeak(mz2find)
                if matchList != []:
                    for mz, I in matchList:
                        timeDependentIntensities.append(
                            [spectrum['scan start time'], I, mz])
        diction = {'rt': [], 'i': [], 'mz': []}
        for rt, i, mz in timeDependentIntensities:
            diction['rt'].append(round(rt, 3))
            diction['i'].append(round(i, 4))
            diction['mz'].append(round(mz, 10))

        json_dict = jsonify(**diction)
        return render_template('ion_chromatogram.html', form=form,
                               filename=filename, json_dict=json_dict,
                               diction=diction)

    return render_template('ion_chromatogram.html', form=form,
                           filename=filename)


@app.route('/original_XML_Tree/<filename>')
def original_XML_Tree(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MSn_Precision=250e-6)
    spectrum = run[1]
    return render_template('original_XML_Tree.html',
                           spectrum_xmlTree=spectrum.xmlTree)


if __name__ == '__main__':
    # app.run(port=4555, debug=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
