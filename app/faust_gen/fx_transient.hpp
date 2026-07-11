/* ------------------------------------------------------------
name: "fx_transient"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxTransient -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxTransient_H__
#define  __FxTransient_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxTransient
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif


class FxTransient : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst1;
	float fConst2;
	float fConst3;
	float fRec1[2];
	float fConst4;
	float fRec0[2];
	float fConst5;
	float fConst6;
	float fRec3[2];
	float fRec2[2];
	FAUSTFLOAT fHslider0;
	float fConst7;
	float fConst8;
	float fConst9;
	float fRec5[2];
	float fConst10;
	float fRec4[2];
	float fConst11;
	float fConst12;
	float fRec6[2];
	FAUSTFLOAT fHslider1;
	
 public:
	FxTransient() {}

	void metadata(Meta* m) { 
		m->declare("analyzers.lib/name", "Faust Analyzer Library");
		m->declare("analyzers.lib/version", "1.2.0");
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxTransient -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_transient.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_transient");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
		m->declare("signals.lib/name", "Faust Signal Routing Library");
		m->declare("signals.lib/version", "1.5.0");
	}

	virtual int getNumInputs() {
		return 2;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		float fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = std::exp(-(1e+03f / fConst0));
		fConst2 = std::exp(-(33.333332f / fConst0));
		fConst3 = 1.0f - fConst2;
		fConst4 = 1.0f - fConst1;
		fConst5 = std::exp(-(2.857143f / fConst0));
		fConst6 = 1.0f - fConst5;
		fConst7 = std::exp(-(4e+01f / fConst0));
		fConst8 = std::exp(-(16.666666f / fConst0));
		fConst9 = 1.0f - fConst8;
		fConst10 = 1.0f - fConst7;
		fConst11 = std::exp(-(2e+03f / fConst0));
		fConst12 = 1.0f - fConst11;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fRec1[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec3[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec5[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec4[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec6[l6] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual FxTransient* clone() {
		return new FxTransient();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_transient");
		ui_interface->addHorizontalSlider("attack", &fHslider1, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("sustain", &fHslider0, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = float(fHslider1);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			float fTemp1 = float(input1[i0]);
			float fTemp2 = std::fabs(std::max<float>(std::fabs(fTemp0), std::fabs(fTemp1)));
			fRec1[0] = std::max<float>(fTemp2, fConst2 * fRec1[1] + fConst3 * fTemp2);
			fRec0[0] = fConst4 * fRec1[0] + fConst1 * fRec0[1];
			fRec3[0] = std::max<float>(fTemp2, fConst5 * fRec3[1] + fConst6 * fTemp2);
			fRec2[0] = fConst4 * fRec3[0] + fConst1 * fRec2[1];
			fRec5[0] = std::max<float>(fTemp2, fConst8 * fRec5[1] + fConst9 * fTemp2);
			fRec4[0] = fConst10 * fRec5[0] + fConst7 * fRec4[1];
			fRec6[0] = fConst12 * fRec5[0] + fConst11 * fRec6[1];
			float fTemp3 = std::pow(1e+01f, 0.05f * (fSlow1 * std::min<float>(1.0f, 0.166667f * std::max<float>(0.0f, 2e+01f * (std::log10(std::max<float>(1.1754944e-38f, fRec6[0] + 1e-09f)) - std::log10(std::max<float>(1.1754944e-38f, fRec4[0] + 1e-09f))))) + fSlow0 * std::min<float>(1.0f, 0.166667f * std::max<float>(0.0f, 2e+01f * (std::log10(std::max<float>(1.1754944e-38f, fRec2[0] + 1e-09f)) - std::log10(std::max<float>(1.1754944e-38f, fRec0[0] + 1e-09f)))))));
			output0[i0] = FAUSTFLOAT(fTemp0 * fTemp3);
			output1[i0] = FAUSTFLOAT(fTemp1 * fTemp3);
			fRec1[1] = fRec1[0];
			fRec0[1] = fRec0[0];
			fRec3[1] = fRec3[0];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fRec4[1] = fRec4[0];
			fRec6[1] = fRec6[0];
		}
	}

};

#endif
