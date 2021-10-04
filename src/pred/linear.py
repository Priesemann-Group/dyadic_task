import torch
import numpy
from configuration import paths


class LinearModel(torch.nn.Module):
    def __init__(self, input_dim=6*2, output_dim=6):
        super(LinearModel, self).__init__()
        self._input_dim = input_dim
        self._linear = torch.nn.Linear(input_dim, output_dim)

    def forward(self, x):
        x = x.view(-1, self._input_dim)
        return self._linear(x)


class Predictor:
    def __init__(self):
        self._model = LinearModel()
        self._model.load_state_dict(torch.load(paths.model_path, map_location=torch.device('cpu')))
        self._model.eval()

    def predict(self, ant_pos, p0_pos, p1_pos):  # TODO two predictions instead of one
        x = torch.zeros((6, 2))
        for ant_idx in range(6):
            x[ant_idx][0] = numpy.linalg.norm(ant_pos[ant_idx] - numpy.array(p0_pos))
            x[ant_idx][1] = numpy.linalg.norm(ant_pos[ant_idx] - numpy.array(p1_pos))
        with torch.no_grad():
            return int(self._model.forward(x).argmax())


