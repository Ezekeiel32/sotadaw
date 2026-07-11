/* ------------------------------------------------------------
name: "cine_brass"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn CineBrass -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __CineBrass_H__
#define  __CineBrass_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS CineBrass
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

static float CineBrass_faustpower2_f(float value) {
	return value * value;
}

class CineBrass : public dsp {
	
 private:
	
	FAUSTFLOAT fButton0;
	float fVec0[2];
	int iRec0[2];
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	FAUSTFLOAT fHslider0;
	float fConst2;
	FAUSTFLOAT fHslider1;
	float fConst3;
	FAUSTFLOAT fHslider2;
	FAUSTFLOAT fHslider3;
	float fConst4;
	FAUSTFLOAT fHslider4;
	float fConst5;
	float fRec3[2];
	float fRec5[2];
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	FAUSTFLOAT fHslider5;
	float fRec2[3];
	
 public:
	CineBrass() {}

	void metadata(Meta* m) { 
		m->declare("compile_options", "-lang cpp -ct 1 -cn CineBrass -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "cine_brass.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "cine_brass");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/saw2ptr:author", "Julius O. Smith III");
		m->declare("oscillators.lib/saw2ptr:license", "STK-4.3");
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
		fConst1 = 1.0f / std::max<float>(1.0f, 0.6f * fConst0);
		fConst2 = 0.7f / std::max<float>(1.0f, 0.8f * fConst0);
		fConst3 = 3.1415927f / fConst0;
		fConst4 = 0.15f / std::max<float>(1.0f, 0.3f * fConst0);
		fConst5 = 1.0f / fConst0;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(0.6f);
		fHslider1 = FAUSTFLOAT(0.7f);
		fHslider2 = FAUSTFLOAT(0.5f);
		fHslider3 = FAUSTFLOAT(0.18f);
		fHslider4 = FAUSTFLOAT(1.1e+02f);
		fHslider5 = FAUSTFLOAT(0.65f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			fRec1[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec3[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec5[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec7[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			fRec9[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec11[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 3; l8 = l8 + 1) {
			fRec2[l8] = 0.0f;
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
	
	virtual CineBrass* clone() {
		return new CineBrass();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("cine_brass");
		ui_interface->addHorizontalSlider("attack", &fHslider3, FAUSTFLOAT(0.18f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("bloom", &fHslider0, FAUSTFLOAT(0.6f), FAUSTFLOAT(0.1f), FAUSTFLOAT(2.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(1.1e+02f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("release", &fHslider2, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.05f), FAUSTFLOAT(2.5f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("swell", &fHslider1, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		int iSlow1 = fSlow0 == 0.0f;
		float fSlow2 = std::max<float>(1.0f, fConst0 * float(fHslider0));
		float fSlow3 = 1.0f / fSlow2;
		float fSlow4 = 1.5e+03f * float(fHslider1) + 3.5e+02f;
		float fSlow5 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow6 = std::max<float>(1.0f, fConst0 * float(fHslider3));
		float fSlow7 = 1.0f / fSlow6;
		float fSlow8 = float(fHslider4);
		float fSlow9 = std::max<float>(1.1920929e-07f, std::fabs(0.501f * fSlow8));
		float fSlow10 = fConst5 * fSlow9;
		float fSlow11 = 1.0f - fConst0 / fSlow9;
		float fSlow12 = std::max<float>(1.1920929e-07f, std::fabs(0.5f * fSlow8));
		float fSlow13 = fConst5 * fSlow12;
		float fSlow14 = 1.0f - fConst0 / fSlow12;
		float fSlow15 = std::max<float>(1.1920929e-07f, std::fabs(1.005f * fSlow8));
		float fSlow16 = fConst5 * fSlow15;
		float fSlow17 = 1.0f - fConst0 / fSlow15;
		float fSlow18 = std::max<float>(1.1920929e-07f, std::fabs(fSlow8));
		float fSlow19 = fConst5 * fSlow18;
		float fSlow20 = 1.0f - fConst0 / fSlow18;
		float fSlow21 = std::max<float>(1.1920929e-07f, std::fabs(0.995f * fSlow8));
		float fSlow22 = fConst5 * fSlow21;
		float fSlow23 = 1.0f - fConst0 / fSlow21;
		float fSlow24 = 0.29411766f * float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow0;
			iRec0[0] = iSlow1 * (iRec0[1] + 1);
			float fTemp0 = float(iRec0[0]);
			fRec1[0] = fSlow0 + fRec1[1] * float(fVec0[1] >= fSlow0);
			float fTemp1 = std::tan(fConst3 * (fSlow4 * std::max<float>(0.0f, std::min<float>(fSlow3 * fRec1[0], std::max<float>(fConst2 * (fSlow2 - fRec1[0]) + 1.0f, 0.3f)) * (1.0f - fConst1 * fTemp0)) + 2e+02f));
			float fTemp2 = 1.0f / fTemp1;
			float fTemp3 = (fTemp2 + 0.8333333f) / fTemp1 + 1.0f;
			float fTemp4 = fSlow10 + fRec3[1] + -1.0f;
			int iTemp5 = fTemp4 < 0.0f;
			float fTemp6 = fSlow10 + fRec3[1];
			fRec3[0] = ((iTemp5) ? fTemp6 : fTemp4);
			float fRec4 = ((iTemp5) ? fTemp6 : fSlow10 + fRec3[1] + fSlow11 * fTemp4);
			float fTemp7 = fSlow13 + fRec5[1] + -1.0f;
			int iTemp8 = fTemp7 < 0.0f;
			float fTemp9 = fSlow13 + fRec5[1];
			fRec5[0] = ((iTemp8) ? fTemp9 : fTemp7);
			float fRec6 = ((iTemp8) ? fTemp9 : fSlow13 + fRec5[1] + fSlow14 * fTemp7);
			float fTemp10 = fSlow16 + fRec7[1] + -1.0f;
			int iTemp11 = fTemp10 < 0.0f;
			float fTemp12 = fSlow16 + fRec7[1];
			fRec7[0] = ((iTemp11) ? fTemp12 : fTemp10);
			float fRec8 = ((iTemp11) ? fTemp12 : fSlow16 + fRec7[1] + fSlow17 * fTemp10);
			float fTemp13 = fSlow19 + fRec9[1] + -1.0f;
			int iTemp14 = fTemp13 < 0.0f;
			float fTemp15 = fSlow19 + fRec9[1];
			fRec9[0] = ((iTemp14) ? fTemp15 : fTemp13);
			float fRec10 = ((iTemp14) ? fTemp15 : fSlow19 + fRec9[1] + fSlow20 * fTemp13);
			float fTemp16 = fSlow22 + fRec11[1] + -1.0f;
			int iTemp17 = fTemp16 < 0.0f;
			float fTemp18 = fSlow22 + fRec11[1];
			fRec11[0] = ((iTemp17) ? fTemp18 : fTemp16);
			float fRec12 = ((iTemp17) ? fTemp18 : fSlow22 + fRec11[1] + fSlow23 * fTemp16);
			fRec2[0] = fSlow24 * (2.0f * (fRec12 - (1.0f - (fRec10 + fRec8))) + 0.7f * (2.0f * fRec6 + -1.0f) + 0.5f * (2.0f * fRec4 + -1.0f) + -1.0f) * std::max<float>(0.0f, std::min<float>(fSlow7 * fRec1[0], std::max<float>(fConst4 * (fSlow6 - fRec1[0]) + 1.0f, 0.85f)) * (1.0f - fSlow5 * fTemp0)) - (fRec2[2] * ((fTemp2 + -0.8333333f) / fTemp1 + 1.0f) + 2.0f * fRec2[1] * (1.0f - 1.0f / CineBrass_faustpower2_f(fTemp1))) / fTemp3;
			float fTemp19 = 0.678f * ((fRec2[2] + fRec2[0] + 2.0f * fRec2[1]) / fTemp3);
			output0[i0] = FAUSTFLOAT(fTemp19);
			output1[i0] = FAUSTFLOAT(fTemp19);
			fVec0[1] = fVec0[0];
			iRec0[1] = iRec0[0];
			fRec1[1] = fRec1[0];
			fRec3[1] = fRec3[0];
			fRec5[1] = fRec5[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			fRec2[2] = fRec2[1];
			fRec2[1] = fRec2[0];
		}
	}

};

#endif
