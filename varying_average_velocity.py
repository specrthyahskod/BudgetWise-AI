from typing import List, Optional

def calculate_ewma(samples: List[float], alpha: float = 0.3) -> float:
    if not samples:
        raise ValueError("Samples list cannot be empty.")
    if not (0 < alpha <= 1):
        raise ValueError("Alpha must be between 0 and 1.")

    ewma = samples[0]

    for sample in samples[1:]:
        ewma = (alpha * sample) + ((1 - alpha) * ewma)

    return ewma


def calculate_projected_energy(
    e_current: float,
    t_current: float,
    t_target: float,
    v_avg: Optional[float] = None,
    power_samples: Optional[List[float]] = None,
    alpha: float = 0.3
    ) -> float:
    if t_target < t_current:
        raise ValueError("Target time T cannot be before current time t_current.")

    time_remaining = t_target - t_current

    if v_avg is None:
        if power_samples and len(power_samples) > 0:
            v_avg = calculate_ewma(power_samples, alpha=alpha)
        else:
            raise ValueError("Must provide either an explicit v_avg or power_samples.")

    e_projected = e_current + (v_avg * time_remaining)

    return e_projected

if __name__ == "__main__":
    current_energy = 15.0   
    current_time = 7.0      
    target_time = 14.0     

    rate_history = [10.0, 12.0, 11.0, 10.5, 12.0, 25.0, 30.0]

    simple_v_avg = sum(rate_history) / len(rate_history)  

    ewma_v_avg = calculate_ewma(rate_history, alpha=0.4)  

    proj_simple = calculate_projected_energy(
        current_energy, current_time, target_time, v_avg=simple_v_avg
    )
    proj_ewma = calculate_projected_energy(
        current_energy, current_time, target_time, power_samples=rate_history, alpha=0.4
    )

    print(f"Simple Mean Rate:  {simple_v_avg:.2f}/unit  -> Projected: {proj_simple:.2f}")
    print(f"EWMA Rate (α=0.4): {ewma_v_avg:.2f}/unit  -> Projected: {proj_ewma:.2f}")