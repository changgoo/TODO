# Daily To-Do List

**Last updated:** 2026-03-19

---

## Q1 — Urgent + Important *(Do First)*
> Deadlines, crises, pressing problems

- [ ] **Tej's turbulence paper**
    - [x] §1 Introduction
    - [x] §2 Methods and Models
        - [x] §2.1 Governing Equations, Numerical Methods, and Initial Conditions
        - [x] §2.2 Point Source Driving
        - [x] §2.3 Fourier Space Driving
        - [x] §2.4 Models
    - [x] §3 Comparison of Driving Methods
        - [x] §3.1 Global Statistics
        - [x] §3.2 Probability Density Functions and Joint Statistics
        - [x] §3.3 Gas Density and Velocity Power Spectra
    - [x] §4 FSD Sensitivity to Correlation Time
        - [x] §4.1 Qualitative Differences
        - [x] §4.2 Time Evolution of Variables
        - [x] §4.3 Probability Density Function Dependence on Correlation Time
    - [x] §5 Summary and Discussion
    
- [ ] **Investigate CR work term**
    - [ ] Compare kinetic flux and CR work term
    - [x] Add thermal gas work term in zprof

- [ ] **Inspect Sink Particle at Shear Boundary**
    - [x] Check violation due to FOFC — inter-meshblock face fluxes not identical; fixed by skipping FOFC
    - [x] Check violation in pure periodic BCs — noverlap_ not large enough to suppress ghost particle formation near active growing particle; fixed by noverlap_=NGHOST
    - [ ] Investigate active-ghost accretion mismatch in shear-periodic BCs


- [ ] **Run simulations**
    - [ ] start run high resolution simulations on Anvil
---

## Q2 — Important, Not Urgent *(Schedule)*
> Planning, growth, long-term projects

- [ ] **Code development**
    - [ ] (fill in specific tasks)

- [ ] **Write TIGRESS-NCR-Paper II**
    - [ ] Finalize outline and section structure
    - [ ] Write introduction
    - [ ] Write methods section
    - [ ] Write results section
    - [ ] Create / finalize figures
    - [ ] Write discussion and conclusions
    - [ ] Revise and edit full draft

- [ ] **Write TIGRESS-CII paper**
    - [ ] Finalize outline and section structure
    - [ ] Write introduction
    - [ ] Write methods section
    - [ ] Write results section
    - [ ] Create / finalize figures
    - [ ] Write discussion and conclusions
    - [ ] Revise and edit full draft

---

## Q3 — Urgent, Not Important *(Delegate or Minimize)*
> Interruptions, some meetings, certain emails

- [ ] **Optimize UCT-HLLD**
    - [ ] Profile current performance / identify bottlenecks
    - [ ] Implement optimizations
    - [ ] Test and validate correctness
    - [ ] Benchmark results

- [ ] **NCR + CR development**
    - [ ] Define requirements and goals
    - [ ] Implement changes
    - [ ] Test
    - [ ] Document

---

## Q4 — Not Urgent, Not Important *(Eliminate or Do Last)*
> Time wasters, low-value tasks

- [ ] (Add tasks here)

---

## Completed
> Move finished tasks here at end of day

- [x] Review ApJ paper — submitted referee report (2026-03-18)
- [x] Cosmia's paper — reviewed full draft (2026-03-11)
- [x] HPE benchmark test — submitted, ran, and reported (2026-03-13)
- [x] Sarah's paper revision — completed (2026-03-16)
- [x] Review MNRAS paper — submitted referee report (2026-04-10)

---

*Tip: Start your day reviewing Q1 and Q2. End your day moving done items to ✅ and reassessing priorities.*
