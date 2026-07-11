/* ------------------------------------------------------------
name: "fx_gate"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxGate -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxGate_H__
#define  __FxGate_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxGate
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


class FxGate : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider0;
	float fConst3;
	FAUSTFLOAT fHslider1;
	float fConst4;
	float fRec2[2];
	float fConst5;
	float fRec1[2];
	FAUSTFLOAT fHslider2;
	float fRec0[2];
	
 public:
	FxGate() {}

	void metadata(Meta* m) { 
		m->declare("analyzers.lib/name", "Faust Analyzer Library");
		m->declare("analyzers.lib/version", "1.2.0");
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxGate -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_gate.dsp");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_gate");
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
		fConst1 = 44.1f / fConst0;
		fConst2 = 1.0f - fConst1;
		fConst3 = std::exp(-(5e+02f / fConst0));
		fConst4 = 1.0f / fConst0;
		fConst5 = 1.0f - fConst3;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(24.0f);
		fHslider1 = FAUSTFLOAT(0.12f);
		fHslider2 = FAUSTFLOAT(-45.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fRec2[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fRec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
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
	
	virtual FxGate* clone() {
		return new FxGate();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_gate");
		ui_interface->addHorizontalSlider("depth", &fHslider0, FAUSTFLOAT(24.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(6e+01f), FAUSTFLOAT(0.5f));
		ui_interface->addHorizontalSlider("rel", &fHslider1, FAUSTFLOAT(0.12f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.005f));
		ui_interface->addHorizontalSlider("thresh", &fHslider2, FAUSTFLOAT(-45.0f), FAUSTFLOAT(-7e+01f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = float(fHslider1);
		int iSlow2 = std::fabs(fSlow1) < 1.1920929e-07f;
		float fSlow3 = ((iSlow2) ? 0.0f : std::exp(-(fConst4 / ((iSlow2) ? 1.0f : fSlow1))));
		float fSlow4 = 1.0f - fSlow3;
		float fSlow5 = float(fHslider2);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			float fTemp1 = float(input1[i0]);
			float fTemp2 = std::fabs(std::max<float>(std::fabs(fTemp0), std::fabs(fTemp1)));
			fRec2[0] = std::max<float>(fTemp2, fRec2[1] * fSlow3 + fTemp2 * fSlow4);
			fRec1[0] = fConst5 * fRec2[0] + fConst3 * fRec1[1];
			fRec0[0] = fConst1 * std::pow(1e+01f, -(0.05f * std::min<float>(fSlow0, 2.0f * std::max<float>(0.0f, fSlow5 - 2e+01f * std::log10(std::max<float>(1.1754944e-38f, fRec1[0] + 1e-09f)))))) + fConst2 * fRec0[1];
			output0[i0] = FAUSTFLOAT(fTemp0 * fRec0[0]);
			output1[i0] = FAUSTFLOAT(fTemp1 * fRec0[0]);
			fRec2[1] = fRec2[0];
			fRec1[1] = fRec1[0];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
