from rootiq.repair.loader import IncidentLoader


def test_loader():

    loader = IncidentLoader()

    incident = loader.load_latest()

    print(incident)



if __name__ == "__main__":

    test_loader()