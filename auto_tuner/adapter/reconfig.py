import numpy as np
from joblib import load


class Reconfiguration:
    def __init__(
        self,
        model_versions: list,
        max_cpu: int,
        capacity_models_paths: dict,
        baseline_accuracies: dict,
        load_times: dict,
        alpha: float,
        beta = 0.2,
    ):
        self.__max_cpu = max_cpu
        self.__model_versions = sorted(model_versions)
        self.__capacity_models = {v: load(capacity_models_paths[v]) for v in self.__model_versions}
        self.__baseline_accuracies = baseline_accuracies
        self.__load_times = load_times
        self.__alpha = alpha
        self.__beta = beta
        self.__min_cpu = 2
    
    def regression_model(self, model_version, cpu):
        assert cpu >= 0, "cpu is a non-negative parameter"
        if cpu == 0:
            return 0
        X = np.array([cpu]).reshape(-1, 1)
        return int(0.8 * self.__capacity_models[model_version].predict(X))
    
    def find_all_valid_options(self, max_cpu, rate, models=None, option=None, options=None):
        if models is None:
            models = self.__model_versions
            
        if option is None:
            option = []
        
        if options is None:
            options = []
        
        if rate <= 0:
            return option[:]
        
        for mi in range(len(models)):
            m = models[mi]
            ms = models[mi+1:]
            for c in range(self.__min_cpu, max_cpu + 1):
                p = self.find_all_valid_options(
                    max_cpu-c, rate - self.regression_model(m, c), ms, option + [(m, c)], options
                )
                if p:
                    options.append(p)
        if models == self.__model_versions:
            return options
        
    def assign_shares_to_options_models(self, options, lmbda):
        options_with_shares = []
        for option in options:
            rate = lmbda
            with_share = []
            for model_choice in sorted(option, key=lambda x: x[0], reverse=True):
                model, cpu = model_choice
                capacity = min(self.regression_model(model, cpu), rate)
                share = capacity / lmbda
                rate -= capacity
                with_share.append((model, cpu, share))
            options_with_shares.append(with_share)
        return options_with_shares

    @staticmethod
    def convert_config_to_dict(config):
        d = {}
        for ms in config:
            m, c, _ = ms
            d[m] = c
        return d
    
    def transition_cost(self, model, current_option, new_option):
        current = self.convert_config_to_dict(current_option)
        new = self.convert_config_to_dict(new_option)
        if model not in new.keys():
            return 0
        if current.get(model) != new.get(model):
            return 1
        return 0

    def load_cost(self, current_option, new_option):
        lc = {v: self.transition_cost(v, current_option, new_option) * self.__load_times[v] for v in self.__model_versions}
        return max(lc.values()) / max(self.__load_times.values())
                

    def find_best_option(self, options_with_shares, prev_option):
        # Todo: add the effect of prev_option
        max_f = -100
        best_option = None
        for option_with_shares in options_with_shares:
            accuracy = 0
            cost = 0
            for model_choice in option_with_shares:
                model, cpu, share = model_choice
                accuracy += share * self.__baseline_accuracies[model]
                cost += cpu
            load_cost = self.load_cost(prev_option, option_with_shares)
            resource_cost = cost / self.__max_cpu
            f = accuracy - (self.__alpha * resource_cost + self.__beta * load_cost)
            if f > max_f:
                max_f = f
                best_option = option_with_shares
        return best_option
    
    def reconfig(self, lmbda, current_option):
        max_cpu = self.__max_cpu
        mamv = sorted(self.__model_versions)[-1]
        for cpu in range(self.__min_cpu, max_cpu + 1):
            if self.regression_model(mamv, cpu) >= lmbda:
                max_cpu = cpu
                break
        # print("max_cpu", max_cpu)
        all_options = self.find_all_valid_options(max_cpu, lmbda)
        all_options_with_shares = self.assign_shares_to_options_models(all_options, lmbda)
        # print("len", len(all_options_with_shares))
        best_option = self.find_best_option(all_options_with_shares, current_option)
        return best_option
    
    def reconfig_msp(self, lmbda, current_option):
        max_cpu = self.__max_cpu
        mamv = sorted(self.__model_versions)[-1]
        for cpu in range(self.__min_cpu, max_cpu + 1):
            if self.regression_model(mamv, cpu) >= lmbda:
                max_cpu = cpu
                break
        all_options = []
        for mv in self.__model_versions:
            for c in range(2, max_cpu + 1):
                if self.regression_model(mv, c) >= lmbda:
                    all_options.append([(mv, c, 1)])
                    break
        best_options = self.find_best_option(all_options, current_option)
        return best_options
