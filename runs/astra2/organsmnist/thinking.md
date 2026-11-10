**Considering design safety**

I'm thinking about how to create a design that’s rotation-safe. To do this, I’ll use symmetric spatial grids, perhaps with center ellipses and squares around a ring, making sure to account for top/bottom and left/right orientations. I want to avoid unsupported orientations. It’s also important to consider some anatomical expectations and how they may relate to the original data pipeline with tools like nibabel and SimpleITK.

**Considering image orientation**

I'm thinking that maybe the right kidney class image is oriented differently due to how cropping coordinates work. The context could be weak, but there might be left/right shape differences. Also, the heart's peripheral air output could depend on how tightly the bounding box crops the heart with the lungs. I'm thinking a sagittal heart box would properly cover the central cardiac silhouette and the posterior corners of the lungs. That makes sense to me!