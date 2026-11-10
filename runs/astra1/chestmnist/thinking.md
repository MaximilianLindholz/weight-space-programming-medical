**Designing coefficients and masks**

I need to create precise coefficients for scoring that normalize average differences. It looks like I can construct masks based on h0, h1, and k2 with shared edits across labels by using scalar broadcasting. However, I can’t just assign one tensor to another, which is a bit tricky, since I’m only working with numbers here. I’ll take care to keep everything clear and organized for this process!

**Simplifying column structure**

I’m figuring out how to simplify this structure! For the outer columns, using a 6:4 ratio gives me a 1 and 5, while for the inner columns, a 5:2 ratio gives me a 2 and 4. Finally, I’m considering the lung columns, with 3 and 4 giving me 6 two blocks. It's all about finding the best arrangement to streamline this!