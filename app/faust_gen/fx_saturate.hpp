/* ------------------------------------------------------------
name: "fx_saturate"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxSaturate -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxSaturate_H__
#define  __FxSaturate_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

/* link with : "" */
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxSaturate
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


class FxSaturate : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	float fConst2;
	FAUSTFLOAT fHslider1;
	float fRec1[2];
	float fVec0[2];
	float fVec1[2];
	FAUSTFLOAT fHslider2;
	float fConst3;
	float fRec0[2];
	float fVec2[2];
	float fVec3[2];
	float fRec2[2];
	
 public:
	FxSaturate() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxSaturate -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_saturate.dsp");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf1:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf1s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf1s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf1s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_saturate");
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
		fConst3 = 3.1415927f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(1.0f);
		fHslider1 = FAUSTFLOAT(6.0f);
		fHslider2 = FAUSTFLOAT(3.5e+03f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fRec1[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fVec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec0[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fVec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec3[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec2[l6] = 0.0f;
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
	
	virtual FxSaturate* clone() {
		return new FxSaturate();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_saturate");
		ui_interface->addHorizontalSlider("drive", &fHslider1, FAUSTFLOAT(6.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(24.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("mix", &fHslider0, FAUSTFLOAT(1.0f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("tone", &fHslider2, FAUSTFLOAT(3.5e+03f), FAUSTFLOAT(5e+02f), FAUSTFLOAT(1e+04f), FAUSTFLOAT(1.0f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider0);
		float fSlow1 = 1.0f - fSlow0;
		float fSlow2 = fConst1 * std::pow(1e+01f, 0.05f * float(fHslider1));
		float fSlow3 = 1.0f / std::tan(fConst3 * float(fHslider2));
		float fSlow4 = 1.0f - fSlow3;
		float fSlow5 = 1.0f / (fSlow3 + 1.0f);
		float fSlow6 = 0.7f * fSlow0;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input0[i0]);
			fRec1[0] = fSlow2 + fConst2 * fRec1[1];
			float fTemp1 = fTemp0 * fRec1[0];
			fVec0[0] = fTemp1;
			float fTemp2 = fTemp1 - fVec0[1];
			float fTemp3 = std::fabs(fVec0[1]);
			float fTemp4 = std::fabs(fTemp1);
			float fTemp5 = ((std::fabs(fTemp2) < 0.0001f) ? tanhf(0.5f * (fTemp1 + fVec0[1])) : (fTemp4 + std::log(std::exp(-(2.0f * fTemp4)) + 1.0f) - (fTemp3 + std::log(std::exp(-(2.0f * fTemp3)) + 1.0f))) / (fTemp1 + 1e-30f * float(fTemp2 == 0.0f) - fVec0[1]));
			fVec1[0] = fTemp5;
			fRec0[0] = -(fSlow5 * (fSlow4 * fRec0[1] - (fTemp5 + fVec1[1])));
			output0[i0] = FAUSTFLOAT(fSlow6 * fRec0[0] + fSlow1 * fTemp0);
			float fTemp6 = float(input1[i0]);
			float fTemp7 = fTemp6 * fRec1[0];
			fVec2[0] = fTemp7;
			float fTemp8 = fTemp7 - fVec2[1];
			float fTemp9 = std::fabs(fVec2[1]);
			float fTemp10 = std::fabs(fTemp7);
			float fTemp11 = ((std::fabs(fTemp8) < 0.0001f) ? tanhf(0.5f * (fTemp7 + fVec2[1])) : (fTemp10 + std::log(std::exp(-(2.0f * fTemp10)) + 1.0f) - (fTemp9 + std::log(std::exp(-(2.0f * fTemp9)) + 1.0f))) / (fTemp7 + 1e-30f * float(fTemp8 == 0.0f) - fVec2[1]));
			fVec3[0] = fTemp11;
			fRec2[0] = -(fSlow5 * (fSlow4 * fRec2[1] - (fTemp11 + fVec3[1])));
			output1[i0] = FAUSTFLOAT(fSlow6 * fRec2[0] + fSlow1 * fTemp6);
			fRec1[1] = fRec1[0];
			fVec0[1] = fVec0[0];
			fVec1[1] = fVec1[0];
			fRec0[1] = fRec0[0];
			fVec2[1] = fVec2[0];
			fVec3[1] = fVec3[0];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
