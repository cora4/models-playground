The largest possible distance from the true value to the centre occurs at either edge of the range:

 $$|e| = |x-\hat{x}| \leq \frac{\Delta}{2}$$

So the quantisation error can range from

 $$-\frac{\Delta}{2} \leq e \leq \frac{\Delta}{2}$$

The variance is

 $$\text{Var}(e)=E[e^2]-E[e]^2$$

The average error is then zero because positive and negative errors cancel.

 Since $E[e]=0$,

 $$\text{Var}(e)=E[e^2]$$

The variance is

$$E[e^2] = \frac{1}{\Delta} \int_{-\Delta/2}^{\Delta/2} e^2 \, de = \frac{\Delta^2}{12}$$

 $$\sigma_e^2 \approx \frac{\Delta^2}{12}$$

If the range being represented is fixed, using fewer bits means fewer levels, which means a larger Δ
And because
 $$\sigma_e^2\propto\Delta^2$$

the quantisation noise grows quadratically with the step size
