# TrafficSimTuner - Simulation Worker Validation

This document demonstrates the successful implementation and execution of the simulation worker component in the **TrafficSimTuner** project.

---

## ✅ Task Summary

We implemented a distributed traffic simulation system where the master component generates simulation permutations, and the worker components run SUMO-based simulations and report results back.

---

## 🚀 Simulation Launched from Web UI

The user inputs expected delays and parameter ranges for acceleration, tau, and startup delay.

**Example input:**

- I2 expected delay: 50 seconds
- I3 expected delay: 20 seconds
- Accel values: `1,2,3`
- Tau values: `1,1.5`
- Startup delay values: `0,0.5,1`

Total simulations launched: **18**

![Form Submitted](md_images/01_form_submitted.png)

---

## 🐳 Worker Containers Launched Automatically

Each permutation is executed in a separate `traffic-sim-worker` Docker container.

![Worker Containers](md_images/02_worker_containers.png)

---

## 📡 Master Receives Input and Waits for Results

The master service logs input parameters and awaits responses from the workers.

![Master Debug Logs - Initial](md_images/03_master_debug_initial.png)

---

## ⏳ Frontend UI Shows Progress in Real Time

As the results come in, the UI updates to reflect the progress of simulations.

![Progress Indicator](md_images/04_progress_shown.png)

---

## 📬 Master Receives Simulation Results

Each worker posts its results to the master. The master computes scores based on delay error and determines the best configuration.

![Results Received in Terminal](md_images/05_results_received.png)

---

## 🏁 Best Match Identified in UI

The system successfully identifies and displays the optimal parameter configuration.

**Example best match:**

- Accel: 1
- Tau: 1.5
- Startup Delay: 0

With intersection delays:

- I2: 45.47 sec
- I3: 20.24 sec

![Best Match in UI](md_images/06_best_result_shown.png)

---

## ✅ Conclusion

The distributed simulation and tuning pipeline was executed successfully. The workers handled the parameter sweeps, SUMO simulation, and result posting, while the master coordinated and evaluated them efficiently.
