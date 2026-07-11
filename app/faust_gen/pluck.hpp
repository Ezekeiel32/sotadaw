/* ------------------------------------------------------------
name: "pluck"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Pluck -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Pluck_H__
#define  __Pluck_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Pluck
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

static float Pluck_faustpower2_f(float value) {
	return value * value;
}

class Pluck : public dsp {
	
 private:
	
	int iVec0[2];
	FAUSTFLOAT fHslider0;
	FAUSTFLOAT fHslider1;
	int fSampleRate;
	float fConst0;
	float fConst1;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec1[2];
	float fConst2;
	float fConst3;
	FAUSTFLOAT fHslider2;
	float fConst4;
	float fRec2[2];
	float fRec5[2];
	float fVec2[2];
	float fConst5;
	int IOTA0;
	float fVec3[4096];
	float fConst6;
	float fRec4[2];
	float fConst7;
	FAUSTFLOAT fHslider3;
	float fRec0[3];
	
 public:
	Pluck() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn Pluck -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "pluck.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/pole:author", "Julius O. Smith III");
		m->declare("filters.lib/pole:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/pole:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "pluck");
		m->declare("oscillators.lib/lf_sawpos:author", "Bart Brouns, revised by Stéphane Letz");
		m->declare("oscillators.lib/lf_sawpos:licence", "STK-4.3");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
		m->declare("oscillators.lib/sawN:author", "Julius O. Smith III");
		m->declare("oscillators.lib/sawN:license", "STK-4.3");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 3.1415927f / fConst0;
		fConst2 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst3 = 1.0f / fConst2;
		fConst4 = 1.0f / fConst0;
		fConst5 = 0.25f * fConst0;
		fConst6 = 0.5f * fConst0;
		fConst7 = 2.4f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(4.0f);
		fHslider1 = FAUSTFLOAT(4.4e+02f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider2 = FAUSTFLOAT(0.5f);
		fHslider3 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec2[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec5[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec2[l5] = 0.0f;
		}
		IOTA0 = 0;
		for (int l6 = 0; l6 < 4096; l6 = l6 + 1) {
			fVec3[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec0[l8] = 0.0f;
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
	
	virtual Pluck* clone() {
		return new Pluck();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("pluck");
		ui_interface->addHorizontalSlider("color", &fHslider0, FAUSTFLOAT(4.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(12.0f), FAUSTFLOAT(0.1f));
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.05f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("freq", &fHslider1, FAUSTFLOAT(4.4e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fHslider1);
		float fSlow1 = std::tan(fConst1 * (fSlow0 * float(fHslider0) + 3e+02f));
		float fSlow2 = 2.0f * (1.0f - 1.0f / Pluck_faustpower2_f(fSlow1));
		float fSlow3 = 1.0f / fSlow1;
		float fSlow4 = (fSlow3 + -1.4142135f) / fSlow1 + 1.0f;
		float fSlow5 = 1.0f / ((fSlow3 + 1.4142135f) / fSlow1 + 1.0f);
		float fSlow6 = float(fButton0);
		float fSlow7 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow8 = std::max<float>(1.1920929e-07f, std::fabs(fSlow0));
		float fSlow9 = fConst4 * fSlow8;
		float fSlow10 = 1.0f - fConst0 / fSlow8;
		float fSlow11 = std::max<float>(fSlow0, 23.44895f);
		float fSlow12 = std::max<float>(2e+01f, std::fabs(fSlow11));
		float fSlow13 = fConst4 * fSlow12;
		float fSlow14 = fConst5 / fSlow12;
		float fSlow15 = std::max<float>(0.0f, std::min<float>(2047.0f, fConst6 / fSlow11));
		int iSlow16 = int(fSlow15);
		int iSlow17 = iSlow16 + 1;
		float fSlow18 = std::floor(fSlow15);
		float fSlow19 = fSlow15 - fSlow18;
		float fSlow20 = fSlow18 + (1.0f - fSlow15);
		float fSlow21 = fConst7 * fSlow0;
		float fSlow22 = float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow6;
			iRec1[0] = (iRec1[1] + (iRec1[1] > 0)) * (fSlow6 <= fVec1[1]) + (fSlow6 > fVec1[1]);
			float fTemp0 = float(iRec1[0]);
			float fTemp1 = fSlow9 + fRec2[1] + -1.0f;
			int iTemp2 = fTemp1 < 0.0f;
			float fTemp3 = fSlow9 + fRec2[1];
			fRec2[0] = ((iTemp2) ? fTemp3 : fTemp1);
			float fRec3 = ((iTemp2) ? fTemp3 : fSlow9 + fRec2[1] + fSlow10 * fTemp1);
			float fTemp4 = ((1 - iVec0[1]) ? 0.0f : fSlow13 + fRec5[1]);
			fRec5[0] = fTemp4 - std::floor(fTemp4);
			float fTemp5 = Pluck_faustpower2_f(2.0f * fRec5[0] + -1.0f);
			fVec2[0] = fTemp5;
			float fTemp6 = fSlow14 * float(iVec0[1]) * (fTemp5 - fVec2[1]);
			fVec3[IOTA0 & 4095] = fTemp6;
			fRec4[0] = 0.999f * fRec4[1] + fTemp6 - (fSlow20 * fVec3[(IOTA0 - iSlow16) & 4095] + fSlow19 * fVec3[(IOTA0 - iSlow17) & 4095]);
			fRec0[0] = fSlow22 * (fSlow21 * fRec4[0] + 0.4f * (2.0f * fRec3 + -1.0f)) * Pluck_faustpower2_f(std::max<float>(0.0f, std::min<float>(fConst3 * fTemp0, fSlow7 * (fConst2 - fTemp0) + 1.0f))) - fSlow5 * (fSlow4 * fRec0[2] + fSlow2 * fRec0[1]);
			float fTemp7 = fSlow5 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp7);
			output1[i0] = FAUSTFLOAT(fTemp7);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec1[1] = iRec1[0];
			fRec2[1] = fRec2[0];
			fRec5[1] = fRec5[0];
			fVec2[1] = fVec2[0];
			IOTA0 = IOTA0 + 1;
			fRec4[1] = fRec4[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
