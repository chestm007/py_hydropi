class OutputMetricCollector:
    def __init__(self, db, reporter):
        super().__init__()
        self.db = db
        self.reporter = reporter

    def push_all(self):
        for type_, group_dict in self.db.controllers.items():
            outputs = []

            for group, controller in group_dict.items():
                if hasattr(controller, '_rising_object') and hasattr(controller, '_falling_object'):
                    outputs.extend([controller._rising_object, controller._falling_object])
                else:
                    if hasattr(controller, 'attached_triggered_outputs'):
                        for d in controller.attached_triggered_outputs.values():
                            outputs.extend(d.get('objects'))
                    outputs.extend(controller.attached_outputs)

                for output in outputs:
                    self.reporter.push(
                        'channel{channel}activated'.format(channel=output.channel),
                        int(output.state)
                    )
