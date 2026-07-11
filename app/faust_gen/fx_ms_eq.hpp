/* ------------------------------------------------------------
name: "fx_ms_eq"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn FxMsEq -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __FxMsEq_H__
#define  __FxMsEq_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS FxMsEq
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

static float FxMsEq_faustpower2_f(float value) {
	return value * value;
}

class FxMsEq : public dsp {
	
 private:
	
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst1;
	FAUSTFLOAT fHslider1;
	float fRec1[3];
	FAUSTFLOAT fHslider2;
	float fRec0[3];
	FAUSTFLOAT fHslider3;
	float fConst2;
	float fConst3;
	FAUSTFLOAT fHslider4;
	float fRec2[2];
	float fRec4[3];
	FAUSTFLOAT fHslider5;
	float fRec3[3];
	FAUSTFLOAT fHslider6;
	
 public:
	FxMsEq() {}

	void metadata(Meta* m) { 
		m->declare("analyzers.lib/name", "Faust Analyzer Library");
		m->declare("analyzers.lib/version", "1.2.0");
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn FxMsEq -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("filename", "fx_ms_eq.dsp");
		m->declare("filters.lib/filterbank:author", "Julius O. Smith III");
		m->declare("filters.lib/filterbank:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/filterbank:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/highshelf:author", "Julius O. Smith III");
		m->declare("filters.lib/highshelf:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/highshelf:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowshelf:author", "Julius O. Smith III");
		m->declare("filters.lib/lowshelf:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowshelf:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "fx_ms_eq");
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
		fConst1 = 3.1415927f / fConst0;
		fConst2 = 44.1f / fConst0;
		fConst3 = 1.0f - fConst2;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(8e+03f);
		fHslider1 = FAUSTFLOAT(2.5e+02f);
		fHslider2 = FAUSTFLOAT(0.0f);
		fHslider3 = FAUSTFLOAT(0.0f);
		fHslider4 = FAUSTFLOAT(0.0f);
		fHslider5 = FAUSTFLOAT(0.0f);
		fHslider6 = FAUSTFLOAT(0.0f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 3; l0 = l0 + 1) {
			fRec1[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 3; l1 = l1 + 1) {
			fRec0[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec2[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 3; l3 = l3 + 1) {
			fRec4[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 3; l4 = l4 + 1) {
			fRec3[l4] = 0.0f;
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
	
	virtual FxMsEq* clone() {
		return new FxMsEq();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("fx_ms_eq");
		ui_interface->addHorizontalSlider("high_freq", &fHslider0, FAUSTFLOAT(8e+03f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(1.4e+04f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("low_freq", &fHslider1, FAUSTFLOAT(2.5e+02f), FAUSTFLOAT(8e+01f), FAUSTFLOAT(6e+02f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("mid_high", &fHslider6, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("mid_low", &fHslider5, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("side_high", &fHslider3, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("side_low", &fHslider2, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("width", &fHslider4, FAUSTFLOAT(0.0f), FAUSTFLOAT(-12.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* input0 = inputs[0];
		FAUSTFLOAT* input1 = inputs[1];
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst1 * float(fHslider0));
		float fSlow1 = FxMsEq_faustpower2_f(fSlow0);
		float fSlow2 = 2.0f * (1.0f - 1.0f / fSlow1);
		float fSlow3 = 1.0f / fSlow0;
		float fSlow4 = (fSlow3 + -1.4142135f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / ((fSlow3 + 1.4142135f) / fSlow0 + 1.0f);
		float fSlow6 = std::tan(fConst1 * float(fHslider1));
		float fSlow7 = 1.0f / FxMsEq_faustpower2_f(fSlow6);
		float fSlow8 = 2.0f * (1.0f - fSlow7);
		float fSlow9 = 1.0f / fSlow6;
		float fSlow10 = (fSlow9 + -1.4142135f) / fSlow6 + 1.0f;
		float fSlow11 = 1.0f / ((fSlow9 + 1.4142135f) / fSlow6 + 1.0f);
		float fSlow12 = std::pow(1e+01f, 0.05f * float(fHslider2));
		float fSlow13 = std::pow(1e+01f, 0.05f * float(fHslider3)) / fSlow1;
		float fSlow14 = fConst2 * std::pow(1e+01f, 0.05f * float(fHslider4));
		float fSlow15 = std::pow(1e+01f, 0.05f * float(fHslider5));
		float fSlow16 = std::pow(1e+01f, 0.05f * float(fHslider6)) / fSlow1;
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			float fTemp0 = float(input1[i0]);
			float fTemp1 = float(input0[i0]);
			fRec1[0] = 0.5f * (fTemp1 - fTemp0) - fSlow11 * (fSlow10 * fRec1[2] + fSlow8 * fRec1[1]);
			float fTemp2 = 2.0f * fRec1[1];
			fRec0[0] = fSlow11 * (fSlow7 * (fRec1[2] + (fRec1[0] - fTemp2)) + fSlow12 * (fRec1[2] + fRec1[0] + fTemp2)) - fSlow5 * (fSlow4 * fRec0[2] + fSlow2 * fRec0[1]);
			float fTemp3 = 2.0f * fRec0[1];
			fRec2[0] = fSlow14 + fConst3 * fRec2[1];
			float fTemp4 = fRec2[0] * (fRec0[2] + fRec0[0] + fTemp3 + fSlow13 * (fRec0[0] + fRec0[2] - fTemp3));
			fRec4[0] = 0.5f * (fTemp1 + fTemp0) - fSlow11 * (fSlow10 * fRec4[2] + fSlow8 * fRec4[1]);
			float fTemp5 = 2.0f * fRec4[1];
			fRec3[0] = fSlow11 * (fSlow7 * (fRec4[2] + (fRec4[0] - fTemp5)) + fSlow15 * (fRec4[2] + fRec4[0] + fTemp5)) - fSlow5 * (fSlow4 * fRec3[2] + fSlow2 * fRec3[1]);
			float fTemp6 = 2.0f * fRec3[1];
			float fTemp7 = fRec3[2] + fRec3[0] + fTemp6 + fSlow16 * (fRec3[0] + fRec3[2] - fTemp6);
			output0[i0] = FAUSTFLOAT(fSlow5 * (fTemp7 + fTemp4));
			output1[i0] = FAUSTFLOAT(fSlow5 * (fTemp7 - fTemp4));
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			fRec2[1] = fRec2[0];
			fRec4[2] = fRec4[1];
			fRec4[1] = fRec4[0];
			fRec3[2] = fRec3[1];
			fRec3[1] = fRec3[0];
		}
	}

};

#endif
