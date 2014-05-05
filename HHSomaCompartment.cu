#include <stdio.h>

#include <cuda_runtime.h>

extern "C"
{
    #include "myriad_debug.h"
	#include "MyriadObject.h"
    #include "Compartment.h"
	#include "HHSomaCompartment.h"
}

#include "Mechanism.cuh"
#include "HHSomaCompartment.cuh"

__device__ void HHSomaCompartment_cuda_simul_fxn(
	void* _self,
	void** network,
	const double dt,
	const double global_time,
	const unsigned int curr_step
	)
{
	struct HHSomaCompartment* self = (struct HHSomaCompartment*) _self;

	double I_sum = 0.0;

	//	Calculate mechanism contribution to current term
	for (unsigned int i = 0; i < self->_.num_mechs; i++)
	{
		struct Mechanism* curr_mech = self->_.my_mechs[i];
		struct Compartment* pre_comp = (struct Compartment*) network[curr_mech->source_id];
		
		//TODO: Make this conditional on specific Mechanism types
		//if (curr_mech->fx_type == CURRENT_FXN)
		I_sum += cuda_mechanism_fxn(curr_mech, self, self, dt, global_time, curr_step);
	}

	//	Calculate new membrane voltage: (dVm) + prev_vm
	self->soma_vm[curr_step] = (dt * (I_sum) / (self->cm)) + self->soma_vm[curr_step - 1];

	return;
}

__device__ compartment_simul_fxn_t HHSomaCompartment_simul_fxn_t = HHSomaCompartment_cuda_simul_fxn;

__device__ __constant__ struct HHSomaCompartmentClass* HHSomaCompartmentClass_dev_t;
__device__ __constant__ struct HHSomaCompartment* HHSomaCompartment_dev_t;