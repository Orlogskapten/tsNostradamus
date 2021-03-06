import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from ..utils.error import (exception_type
                            , check_is_int)


class tunnelSnake:

    def __init__(self, serie, shift: int, threshold):
        self.serie= serie
        self.shift= shift
        self.threshold= threshold

        # Control type
        exception_type(self.serie, (list, tuple, np.ndarray))
        exception_type(self.threshold, (int, float))
        check_is_int(self.shift)

        assert len(self.serie) >= self.shift * 2
        pass

    def __moving_average(self) -> np.array:
        cumsum_array= np.cumsum(self.serie)
        cumsum_array[self.shift:]= cumsum_array[self.shift:] - cumsum_array[:-self.shift]
        cumsum_array[:self.shift]= cumsum_array[self.shift: self.shift * 2][::-1]
        cumsum_array = cumsum_array / self.shift
        return cumsum_array

    def __augmented_borne_ma(self):
        moving_average_serie= self.__moving_average()
        # On ne veut pas garder la dernière valeur de la moyenne mobile pour décaler de 1 vers la
        # la droite notre moyenne mobile, pour qu'une forte valeur soit prise en compte
        # dans la moyenne la période d'après et pas sur la période d'observation de la valeur aberante
        moving_average_serie= np.append(moving_average_serie[0], moving_average_serie[:-1])

        up_aug_ma= moving_average_serie.copy()
        up_aug_ma = up_aug_ma * (1 + self.threshold)

        down_aug_ma = moving_average_serie.copy()
        down_aug_ma = down_aug_ma * (1 - self.threshold)

        return up_aug_ma, down_aug_ma;

    def fit_transform(self, verbose: bool= True) -> np.array:
        """

        :param verbose:
        :return: array, serie without outlier values
        """
        # Control serie type and serie content type
        self.serie = np.array(self.serie).astype(float)

        up_aug_ma, down_aug_ma = self.__augmented_borne_ma()

        # Which values are sup / inf to the augmented MA
        # and get the augmented MA value when it's True
        boolean_up = self.serie >= up_aug_ma
        boolean_down = self.serie < down_aug_ma
        boolean_serie = boolean_up * up_aug_ma + boolean_down * down_aug_ma

        # Get the index of values we have to change
        index_to_change = (boolean_serie != 0).nonzero()

        if verbose:
            # We removed the shift first values, because they are always into index_to_change
            print("Values at place {} were changed.".format(index_to_change[0]))

        # Replace from inital array
        treated_serie = self.serie.copy()
        treated_serie[index_to_change[0]] = boolean_serie[index_to_change[0]]

        return treated_serie


    def plot(self, figsize: tuple= (8, 5)) -> None:
        sns.set()
        up_aug_ma, down_aug_ma = self.__augmented_borne_ma()

        plt.figure(figsize= figsize)

        plt.plot(self.fit_transform(verbose= False), label= "Transformed serie"
                 , c= "darkblue", linestyle= "--", linewidth= 0.9)
        plt.plot(self.serie, label= "Original serie", c= "black")
        plt.plot(up_aug_ma, label= "Boundaries", c= "orange")
        plt.plot(down_aug_ma, c= "orange")

        plt.xlabel("Index")
        plt.ylabel("Values")
        plt.legend()

        plt.show()
        pass