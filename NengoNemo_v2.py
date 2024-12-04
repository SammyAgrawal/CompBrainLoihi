%matplotlib inline
import matplotlib.pyplot as plt
import numpy as np

import nengo
from nengo.utils.matplotlib import rasterplot

class Area: 
    def __init__(self, network, name, n, k, beta=0.05, w=0, explicit=None):
        with network: 
            neurons = nengo.Ensemble(n, dimensions=k,
                        #intercepts=Uniform(-0.5, -0.5), # Set intercept to 0.5
                        #max_rates=Uniform(100, 100), # Set the maximum firing rate of the neuron to 100hz
                        # encoders=[[1]], # Set the neuron's firing rate to increase for positive input
                        label=name
            )

        self.winners = self.extract_activity(neurons)
        self.fixed_assembly = False

        # dummy variables
        self.num_ever_fired = 0
        
    def _update_winners(self):
        self.winners = self._new_winners

    def update_beta_by_stimulus(self, name, new_beta):
        pass

    def update_area_beta(self, name, new_beta):
        pass
        
    def fix_assembly(self):
        if not self.winners:
            raise ValueError(f'Area {self.name!r} does not have assembly; cannot fix.')
            return
        self.fixed_assembly = True
    def unfix_assembly(self):
        self.fixed_assembly = False
    
    def get_num_ever_fired(self):
        return self.num_ever_fired


class Brain:
    def __init__(self, p, save_size=True, save_winners=False, seed=0):
        self.p = p

    def add_stimulus(self, stimulus_name, size):
        pass

    def add_area(self, area_name, n, k, beta):
        self.add_explicit_area(area_name, n, k, beta, custom_inner_p=self.p, custom_out_p=self.p, custom_in_p=self.p)
    
    def add_explicit_area(self, area_name, n, k, beta, custom_inner_p=None, custom_out_p=None, custom_in_p=None):
        pass

    def update_plasticity(self, from_area, to_area, new_beta):
        pass
    
    def update_plasticities(self, area_update_map=EMPTY_MAPPING, stim_update_map=EMPTY_MAPPING):
        # area_update_map consists of area1: list[ (area2, new_beta) ]
        # represents new plasticity FROM area2 INTO area1
        for to_area, update_rules in area_update_map.items():
            for from_area, new_beta in update_rules:
                self.update_plasticity(from_area, to_area, new_beta)
    
        for area, update_rules in stim_update_map.items():
            the_area = self.area_by_name[area]
            for stim, new_beta in update_rules:
                the_area.beta_by_stimulus[stim] = new_beta
        
    def activate(self, area_name, index):
        # need to treat index as some specific set of encoding vectors (E * index_sparse) 
        pass

    def project(self, areas_by_stim, dst_areas_by_src_area, verbose=0):
        stim_in = collections.defaultdict(list)
        area_in = collections.defaultdict(list)
        for stim, areas in areas_by_stim.items():
            if stim not in self.stimulus_size_by_name:
                raise IndexError(f"Not in brain.stimulus_size_by_name: {stim}")
            for area_name in areas:
                if area_name not in self.area_by_name:
                  raise IndexError(f"Not in brain.area_by_name: {area_name}")
                stim_in[area_name].append(stim)
        for from_area_name, to_area_names in dst_areas_by_src_area.items():
            if from_area_name not in self.area_by_name:
                raise IndexError(from_area + " not in brain.area_by_name")
            for to_area_name in to_area_names:
                if to_area_name not in self.area_by_name:
                    raise IndexError(f"Not in brain.area_by_name: {to_area_name}")
                area_in[to_area_name].append(from_area_name)
        to_update_area_names = stim_in.keys() | area_in.keys()
        
        for area_name in to_update_area_names:
            area = self.area_by_name[area_name]
            num_first_winners = self.project_into(area, stim_in[area_name], area_in[area_name], verbose)
            area.num_first_winners = num_first_winners
            if self.save_winners:
                area.saved_winners.append(area._new_winners)
        
        # once everything is done, for each area in to_update: area.update_winners()
        for area_name in to_update_area_names:
            area = self.area_by_name[area_name]
            area._update_winners()
            if self.save_size:
                area.saved_w.append(area.w)
    
    def project_into(self, target_area, from_stimuli, from_areas, verbose=0):
        pass
        
    
