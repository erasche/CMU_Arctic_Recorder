# CMU Arctic Recorder

Ever needed to record a copy of [CMU Arctic](http://festvox.org/cmu_arctic/)? 
Sure! Who hasn't, right? ... right? Anyway. For those us of working on our
voices one way or another, here's a handy dandy script to prompt you for
each of the thousand or so sentences in arctic, and store those to
separate `.wav` files for further processing/analysis/etc.

Features a pleasant terminal prompt with cute ASCII art volume graph, since the
recording automatically breaks on a pause longer than two seconds.

```console
[arctic_a0019 18/1132]> I followed the line of the proposed railroad, looking for chances.




*  *      
****      
*****     
*******   
*******   
**********
```

## LICENSE

The bulk of the python script is from
[stackOverflow](http://stackoverflow.com/a/16385946), only with threshold
adjusted for my mic, that's under cc-wiki.
