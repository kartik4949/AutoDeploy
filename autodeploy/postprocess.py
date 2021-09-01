from register import POSTPROCESS

@POSTPROCESS.register_module(name='some_custom_postprocess_fxn')
def custom_postprocess_fxn(output):
  output = {'out': output[0],
            'probablity': output[1],
            'status': 200}
  return output
