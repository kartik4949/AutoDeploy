from register.register import INFERE


class InfereBuilder:
  def __init__(self, config, model):
    self.config = config
    self.model = model
    _infere_class = INFERE.get(self.config.model.model_type)
    self.infere_class = _infere_class(config, model)

  def get_inference(self, input):
    return self.infere_class.infere(input)
