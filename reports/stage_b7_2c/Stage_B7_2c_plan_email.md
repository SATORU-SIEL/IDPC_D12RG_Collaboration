# B7.2c proposal: Directed-Provenance C Reconstruction Audit

Dear Luke, Marcel, C.A.T., Thomas, Chris, all,

Following the B7.2b result and the subsequent comments from Luke/C.A.T. and Marcel, I would like to propose B7.2c.

My reading is that Luke/C.A.T. and Marcel, although approaching the problem from somewhat different directions, are converging on the same immediate empirical question.

Luke/C.A.T. emphasized:

- endpoint-local direction pairing;
- train/test correspondence preservation;
- directed transport closure;
- provenance-preserving correspondence;

and suggested that the next step should be reconstruction of the missing directed-provenance structure, rather than an immediate return to C12.

Marcel similarly emphasized that the remaining boundary appears to be carried more by correspondence preservation than by a state or scalar value, and that the immediate task is to identify the correspondence structure itself.

I agree with that assessment.

B7.2a and B7.2b showed that the remaining boundary is not explained by:

- memory alone;
- direction labels alone;
- fixed masks alone;
- static scalar closure.

At the same time, the following remained important:

- endpoint-local direction pairing;
- train/test correspondence preservation;
- directed transport closure;
- provenance-preserving correspondence.

Therefore the next question seems straightforward:

Can we reconstruct the remaining endpoint-local side/direction structure without directly using endpoint-adjacent O1/O2 itself?

B7.2c is intended to test exactly that question.

## B7.2c

Directed-Provenance C Reconstruction Audit

## Central Question

Can a Directed-Provenance C representation reproduce the endpoint-local O1/O2 advantage without directly using endpoint-adjacent O1/O2 values?

## Candidate Representations

Directed C preserves:

- side identity;
- direction identity.

Directed-Provenance C preserves:

- side identity;
- direction identity;
- endpoint pairing;
- train/test correspondence;
- construction provenance.

## Controls

- direction swap
- direction relabel
- side swap
- side shuffle
- endpoint pairing swap
- train/test mismatch
- fixed mask
- static scalar closure
- directed transport closure

## Primary Criterion

Can Directed-Provenance C reproduce the endpoint-local O1/O2 advantage without directly using endpoint-adjacent O1/O2 values?

## Primary Classification

- directed_c_sufficient
- directed_provenance_required
- endpoint_pairing_required
- train_test_correspondence_required
- directed_transport_required
- fixed_mask_sufficient
- unresolved_endpoint_structure

## Positioning

B7.2c is not intended as an ontology comparison.

It is also not intended as a C12 confirmation test.

Following the direction suggested by Luke/C.A.T. and Marcel, B7.2c is intended as a reconstruction audit:

Can the endpoint-local side/direction structure that survived B7.2b be reconstructed as a Directed-Provenance C representation?

Only after answering that question would it make sense to return to broader issues such as C12/Phi24 reconnection, factorisation-path invariance, recursive closure, or other higher-level interpretations.

Best,

Satoru
