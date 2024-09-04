"""
Functions to load the indices and access the data online
"""

import pickle

DATAFILE = __file__[:-13] + "data/data.pkl"


with open(DATAFILE, "rb") as f:
    DATA = pickle.load(f)


def get_patient_ids():
    """
    Return a tuple with all the patients
    """
    return tuple((patient_id for patient_id in DATA))


def get_dataset_by_id(patient_ids) -> dict:
    """
    Return dict with the datasets associated to a
    patient or a list of patients.
    """
    # Simulate the load of the data.
    # TODO: replace this by a routine that actually
    # load data from the repo.
    import numpy
    from numpy.random import random

    if isinstance(patient_ids, str):
        patient_ids = [patient_ids]

    offsets = [int(patient_id[1:]) for patient_id in patient_ids]
    ms = [
        numpy.array(
            [
                [numpy.exp(-(((i + j + offset) % offset) ** 2) / 32) for i in range(64)]
                for j in range(64)
            ]
        )
        for offset in offsets
    ]

    x = [
        m.dot(
            random(
                (
                    64,
                    1000,
                )
            )
        )
        for m in ms
    ]
    return {patient_id: x[indx] for indx, patient_id in enumerate(patient_ids)}
