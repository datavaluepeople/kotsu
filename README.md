# comp
Lightweight framework for structured and repeatable model validation


## Draft API

Generally the API, and even lots of the implementation, will follow as in `truman`: https://github.com/datavaluepeople/truman  
See the `truman` API in usage here: https://github.com/datavaluepeople/carrey/blob/main/notebooks/agent.ipynb


The parts which will differ are:
- `agent` becomes `model`
- `env` becomes `validation`
- `validation` functions will take a `model` class/factory and `kwargs` not an instance of such, as validation functions
will likely want to instantiate a model multiple times i.e. when doing a k-fold validation
- Removing constraints on the `validation` (`env`) interface; likely just:
```
# in comp.run

def run_specific_validation(validation, model_class_or_factory, run_params):  # function name WIP
    """Run validation of model."""
    validation.run(model_class_or_factory)
    # store the results of the validation

```
This fully leaves open and general the protocol for model and the validation implementation, other than validations
needing a `run` method which takes a model factory. I think this is right level of generality needed.
- Fully general `store` outputs, to enable any validation function and model

### Model registry

```
topic_tagging_model_registry = comp.model_registration.ModelRegistry()

topic_tagging_model_registry.register(
    id="TuplesCountsMapping-v1",
    entry_point=topic.models.Tuples,
    kwargs={"mapping_file": "mapping_v1"}
)

topic_tagging_model_registry.register(
    id="TuplesCountsMapping-v2",
    entry_point=topic.models.Tuples,
    kwargs={"mapping_file": "mapping_v2"}
)
```

### Validation registry

```
topic_tagging_validation_registry = comp.validation_registration.ValidationRegistry()

topic_tagging_validation_registry.register(
    id="5-fold-data-up-to-March-v0",
    entry_point=topic.validations.KFold,
    kwargs={"folds": 5, "data_limit": "March"}
)

topic_tagging_validation_registry.register(
    id="5-fold-data-up-to-June-v0",
    entry_point=topic.validations.KFold,
    kwargs={"folds": 5, "data_limit": "June"}
)
```

### Run

```
comp.run(topic_tagging_validation_registry, topic_tagging_model_registry, {"output_directory": "../topic_tagging_validatin_store"}

# then read and visualise results of validation from the designated store
```

### Store

Again, will follow as implemented in `truman` except that in `comp` it will be a lot more general.

A `validation` should output a table row per `model` it validates on which summarises the results for that validation-model
combo. A `validation` may also output a more comprehensive set of results, as either a dict (stored as json) or a dataframe
stored as a table.
And `models` may output data on it's "history"/"internals" (haven't found good name for this), which can again be dict or dataframe,
and would likely including detailing of the models training process and any pertinent info for understanding the model's
functioning.

### Typing/protocols

It would be beneficial for a `validation` module, or the higher level module contains code pertaining to a certain perdiction
task, if it defined `Protocol`s for the models and the validations, thus ensuring compatibility. I don't think we should try
to have `comp` enforce any of this though - `comp` should just run the `validations` against the `models` you specified, and
if they don't work together that's on the user. The user can define any `Protocols` and apply them to their code to get
type hint checking if they wish.
