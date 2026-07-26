from rootiq.repair.rootcause import RootCauseEngine



class RepairAnalyzer:


    def __init__(self):

        self.engine = RootCauseEngine()



    def analyze(self, incident):

        return self.engine.analyze(
            incident.get("issues", [])
        )