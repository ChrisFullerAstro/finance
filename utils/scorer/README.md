# Scorer

This is a package designed to be used to score and tune category_selector.


## Testing

Using the ```suggest_category``` method of category_selector.py we have drawn a number of samples in temral order. Where the number of smaples if the number of samples that ```suggest_category``` can use to make a guess which is the most likely lable.

![Alt text](full_test.png?raw=true "All Samples Accepted")

The above showes that after 200 samples the accuarcy (of accepting all transactions) is arround 80%.


Futher to this I ran some tests to understand how the similarty threahold is realated to the classfication accuarcy. Thus, we could figure out what the relationship was and offer the user a chance to set the classfication likelyhood rather than text similarity as this is a more intuative stat.

![Alt text](auto_vs_acc.png?raw=true "All Samples Accepted")

Above we can see that at a similarity threahold 0.2 and below there is a 97% Classfication accuarcy for automatically accepted transations. This was for 200 traning samples as shown above behond this it is not significantly more accuart.


![Alt text](auto_vs_acc_n_samples.png?raw=true "All Samples Accepted")

The above is plotted now with each line corrosponding to the number of samples where the plot is Acceptance threhold vs accuarcy.



## Futher Work

* It would be interesting to see the fraction that were automatically classfied vs not.

* Also plot a random classfication on the above to see how much better we do.

* Try different recipes for ```suggest_category``` and see how the stats differ.

* Try random test train split to see how much temporal selection effects the stats.
