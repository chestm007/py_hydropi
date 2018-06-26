class SensorMetricCollector:
    def __init__(self, db, reporter):
        super().__init__()
        self.db = db
        self.reporter = reporter

    def push_all(self):
        for id, sensor in self.db._inputs.items():
            self.reporter.push(id, sensor.value)
