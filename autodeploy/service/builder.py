from register.register import INFERE


class InfereBuilder:
  def __init__(self, config, model):
    self.config = config
    self.model = model
    self.multi_model = False
    if len(model) > 1:
      self.multi_model = True
      logger.info('running multiple models..')

    _infere_class = INFERE.get(self.config.model.model_type)
    _infere_class_instances = []
    for mod in model:
       _infere_class_instances.append(_infere_class(config, mod)

  def _get_model_id_from_split(self):
    return np.choice(np.arange())


  def get_inference(self, input):
    return self.infere_class.infere(input)
