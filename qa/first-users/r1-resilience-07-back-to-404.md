# r1-resilience-07-back-to-404

- **step:** 07 — browser Back mid shortener flow
- **observed:** Alt+ArrowLeft no-op in embedded browser. `history.back()` left shortener for `/tools/calculator`, which is a 404 ("This path isn't on Gleb.Y."). History includes a dead calculator URL from earlier direct navigation.
- **intended action:** Mid-flow Back should land on a usable prior page.
