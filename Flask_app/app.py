import os
import sys
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
from werkzeug import secure_filename
import pymzml

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




# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/peak_finding/<filename>')
def peak_finding(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MS1_Precision=5e-6,
                            MSn_Precision=20e-6)
    lst = []
    for spectrum in run:
        if spectrum["ms level"] == 2:
            peak_to_find = spectrum.hasPeak(1016.5404)
            lst.append(peak_to_find)
    if not lst:
        return "No peak found."
    return render_template('peak_to_find.html', lst=lst)
    # return send_from_directory(app.config['UPLOAD_FOLDER'],
    #                            filename)


@app.route('/plot_spectrum/<filename>')
def plot_spectrum(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MSn_Precision=25e-6)
    p = pymzml.plot.Factory()
    for spec in run:
        p.newPlot()
        p.add(spec.peaks, color=(200, 00, 00), style='circles')
        p.add(spec.centroidedPeaks, color=(00, 00, 00), style='sticks')
        p.add(spec.reprofiledPeaks, color=(00, 255, 00), style='circles')
        p.save(filename="static/tmp/plotAspect.xhtml")
        # p.save(filename="templates/plotAspect.xhtml")
    # return render_template('plotAspect.xhtml')

    return render_template('plotAspect.html',
                           fig=url_for('static',
                                       filename='tmp/plotAspect.xhtml'))


@app.route('/highest_peaks/<filename>')
def highest_peaks(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MS1_Precision=5e-6,
                            MSn_Precision=20e-6)
    for spectrum in run:
        if spectrum["ms level"] == 2:
            if spectrum["id"] == 1770:
                for mz, i in spectrum.highestPeaks(5):
                    return mz, i
        else:
            return "Peak does not exist."


@app.route('/extract_Ion_Chromatogram/<filename>')
def extract_Ion_Chromatogram(filename):
    MASS_2_FOLLOW = 810.53
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MS1_Precision=20e-6, MSn_Precision=20e-6)
    timeDependentIntensities = []
    for spectrum in run:
        if spectrum['ms level'] == 1:
            matchList = spectrum.hasPeak(MASS_2_FOLLOW)
            if matchList != []:
                for mz, I in matchList:
                    timeDependentIntensities.append(
                        [spectrum['scan start time'], I, mz])
    diction = {'rt': [], 'i': [], 'mz': []}
    for rt, i, mz in timeDependentIntensities:
        diction['rt'].append(round(rt, 3))
        diction['i'].append(round(i, 4))
        diction['mz'].append(round(mz, 10))
    return jsonify(diction)


@app.route('/original_XML_Tree/<filename>')
def original_XML_Tree(filename):
    filepath = get_abs_path() + "/uploads/" + filename
    run = pymzml.run.Reader(filepath, MSn_Precision=250e-6)
    spectrum = run[1]
    return render_template('original_XML_Tree.html',
                           spectrum_xmlTree=spectrum.xmlTree)

if __name__ == '__main__':
    app.run(port=4555, debug=True)
