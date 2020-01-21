import os

import json
import pymongo
import pandas as pd 
import numpy as np 

from flask import Flask, jsonify, render_template 

##############################################################
# Database Setup
##############################################################

# Extracting Json data
###########################
with open("Documents/Github/plotly-challenge/samples.json", "r") as read_file:
    data = json.load(read_file)

# Connecting to Mongodb
###########################
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Loading data to Mongodb
###########################
db = client.bellybutton
collection = db.Samples
collection.insert_one(data)

# Flask API
###########################
app = Flask(__name__)
app.config["DEBUG"] = True

# reflect existing database into a new model
#Base = automap_base()
# reflect the tables
#Base.prepare(db.engine, reflect=True)

# NOTES: how to select the name value from every object in the metadata array 

# Save references to each table
Samples_Metadata = collection.find({}, { 'metadata': True, "_id": False})
#Metadata_Sample = collection.find({}, { 'metadata.sample': True, "_id": False})
#Metadata_Ethnicity = collection.find({}, { 'metadata.ethnicity': True, "_id": False})
#Metadata_Gender = collection.find({}, { 'metadata.gender': True, "_id": False})
#Metadata_Age = collection.find({}, { 'metadata.age': True, "_id": False})
#Metadata_Location = collection.find({}, { 'metadata.location': True, "_id": False})
#Metadata_BBType = collection.find({}, { 'metadata.bbtype': True, "_id": False})
#Metadata_WFreq = collection.find({}, { 'metadata.WFreq': True, "_id": False})


Samples = collection.find({}, { 'samples': True, "_id": False})
Names = collection.find({}, { 'names': True, "_id": False})

#d = list(station_collection.find({},{"_id": False}))

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")


# App routes
@app.route("/names")
def names():
    """Return a list of sample names."""
    # Return a list of the column names (sample names)
    return jsonify(list(Names))


@app.route("/metadata/<sample>")
def sample_metadata(sample):
    """Return the MetaData for a given sample."""
    results = collection.find({'metadata': { 'id': sample}}, { 'metadata': True, "_id": False})

    # Create a dictionary entry for each row of metadata information
    print(results)
    return jsonify(list(results))


@app.route("/samples/<sample>")
def samples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    stmt = db.session.query(Samples).statement
    df = pd.read_sql_query(stmt, db.session.bind)

    # Filter the data based on the sample number and
    # only keep rows with values above 1
    sample_data = df.loc[df[sample] > 1, ["otu_id", "otu_label", sample]]

    # Sort by sample
    sample_data.sort_values(by=sample, ascending=False, inplace=True)

    # Format the data to send as json
    data = {
        "otu_ids": sample_data.otu_id.values.tolist(),
        "sample_values": sample_data[sample].values.tolist(),
        "otu_labels": sample_data.otu_label.tolist(),
    }
    return jsonify(data)


if __name__ == "__main__":
    app.run()