/* ------------------------------------------------------------
name: "pad_motion"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn PadMotion -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __PadMotion_H__
#define  __PadMotion_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS PadMotion
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

class PadMotionSIG0 {
	
  private:
	
	int iVec0[2];
	int iRec0[2];
	
  public:
	
	int getNumInputsPadMotionSIG0() {
		return 0;
	}
	int getNumOutputsPadMotionSIG0() {
		return 1;
	}
	
	void instanceInitPadMotionSIG0(int sample_rate) {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			iRec0[l1] = 0;
		}
	}
	
	void fillPadMotionSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec0[0] = 1;
			iRec0[0] = (iVec0[1] + iRec0[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec0[0]));
			iVec0[1] = iVec0[0];
			iRec0[1] = iRec0[0];
		}
	}

};

static PadMotionSIG0* newPadMotionSIG0() { return (PadMotionSIG0*)new PadMotionSIG0(); }
static void deletePadMotionSIG0(PadMotionSIG0* dsp) { delete dsp; }

static float ftbl0PadMotionSIG0[65536];
static float PadMotion_faustpower2_f(float value) {
	return value * value;
}

class PadMotion : public dsp {
	
 private:
	
	int iVec1[2];
	FAUSTFLOAT fHslider0;
	int fSampleRate;
	float fConst0;
	float fConst1;
	float fRec1[2];
	FAUSTFLOAT fHslider1;
	float fConst2;
	FAUSTFLOAT fHslider2;
	float fRec2[2];
	FAUSTFLOAT fButton0;
	float fVec2[2];
	int iRec3[2];
	float fConst3;
	float fRec4[2];
	float fConst4;
	float fConst5;
	float fConst6;
	FAUSTFLOAT fHslider3;
	FAUSTFLOAT fHslider4;
	float fRec7[2];
	float fRec9[2];
	float fRec11[2];
	float fRec13[2];
	float fVec3[2];
	float fRec6[2];
	float fRec5[3];
	FAUSTFLOAT fHslider5;
	
 public:
	PadMotion() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn PadMotion -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "pad_motion.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
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
		m->declare("name", "pad_motion");
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
		PadMotionSIG0* sig0 = newPadMotionSIG0();
		sig0->instanceInitPadMotionSIG0(sample_rate);
		sig0->fillPadMotionSIG0(65536, ftbl0PadMotionSIG0);
		deletePadMotionSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		fConst1 = 1.0f / fConst0;
		fConst2 = 3.1415927f / fConst0;
		fConst3 = 1.0f / std::max<float>(1.0f, 1.2f * fConst0);
		fConst4 = std::max<float>(1.0f, 0.6f * fConst0);
		fConst5 = 1.0f / fConst4;
		fConst6 = 0.2f / std::max<float>(1.0f, fConst0);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(0.11f);
		fHslider1 = FAUSTFLOAT(1.8e+03f);
		fHslider2 = FAUSTFLOAT(0.07f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider3 = FAUSTFLOAT(0.007f);
		fHslider4 = FAUSTFLOAT(1.1e+02f);
		fHslider5 = FAUSTFLOAT(0.5f);
	}
	
	virtual void instanceClear() {
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iVec1[l2] = 0;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			fRec1[l3] = 0.0f;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			fRec2[l4] = 0.0f;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fVec2[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 2; l6 = l6 + 1) {
			iRec3[l6] = 0;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			fRec4[l7] = 0.0f;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec7[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec9[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 2; l10 = l10 + 1) {
			fRec11[l10] = 0.0f;
		}
		for (int l11 = 0; l11 < 2; l11 = l11 + 1) {
			fRec13[l11] = 0.0f;
		}
		for (int l12 = 0; l12 < 2; l12 = l12 + 1) {
			fVec3[l12] = 0.0f;
		}
		for (int l13 = 0; l13 < 2; l13 = l13 + 1) {
			fRec6[l13] = 0.0f;
		}
		for (int l14 = 0; l14 < 3; l14 = l14 + 1) {
			fRec5[l14] = 0.0f;
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
	
	virtual PadMotion* clone() {
		return new PadMotion();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("pad_motion");
		ui_interface->addHorizontalSlider("depth", &fHslider1, FAUSTFLOAT(1.8e+03f), FAUSTFLOAT(0.0f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(1e+01f));
		ui_interface->addHorizontalSlider("detune", &fHslider3, FAUSTFLOAT(0.007f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.03f), FAUSTFLOAT(0.0005f));
		ui_interface->addHorizontalSlider("drift", &fHslider2, FAUSTFLOAT(0.07f), FAUSTFLOAT(0.0f), FAUSTFLOAT(0.5f), FAUSTFLOAT(0.005f));
		ui_interface->addHorizontalSlider("freq", &fHslider4, FAUSTFLOAT(1.1e+02f), FAUSTFLOAT(3e+01f), FAUSTFLOAT(1.5e+03f), FAUSTFLOAT(0.01f));
		ui_interface->addHorizontalSlider("gain", &fHslider5, FAUSTFLOAT(0.5f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("motion", &fHslider0, FAUSTFLOAT(0.11f), FAUSTFLOAT(0.02f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.005f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = fConst1 * float(fHslider0);
		float fSlow1 = 0.5f * float(fHslider1);
		float fSlow2 = fConst1 * float(fHslider2);
		float fSlow3 = float(fButton0);
		int iSlow4 = fSlow3 == 0.0f;
		float fSlow5 = float(fHslider3);
		float fSlow6 = float(fHslider4);
		float fSlow7 = std::max<float>(1.1920929e-07f, std::fabs(fSlow6 * (fSlow5 + 1.0f)));
		float fSlow8 = fConst1 * fSlow7;
		float fSlow9 = 1.0f - fConst0 / fSlow7;
		float fSlow10 = std::max<float>(1.1920929e-07f, std::fabs(fSlow6));
		float fSlow11 = fConst1 * fSlow10;
		float fSlow12 = 1.0f - fConst0 / fSlow10;
		float fSlow13 = std::max<float>(1.1920929e-07f, std::fabs(fSlow6 * (1.0f - fSlow5)));
		float fSlow14 = fConst1 * fSlow13;
		float fSlow15 = 1.0f - fConst0 / fSlow13;
		float fSlow16 = std::max<float>(1.1920929e-07f, std::fabs(2.0f * fSlow6 * (0.5f * fSlow5 + 1.0f)));
		float fSlow17 = fConst1 * fSlow16;
		float fSlow18 = 1.0f - fConst0 / fSlow16;
		float fSlow19 = float(fHslider5);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec1[0] = 1;
			int iTemp0 = 1 - iVec1[1];
			float fTemp1 = ((iTemp0) ? 0.0f : fSlow0 + fRec1[1]);
			fRec1[0] = fTemp1 - std::floor(fTemp1);
			float fTemp2 = std::tan(fConst2 * (fSlow1 * (ftbl0PadMotionSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec1[0]), 65535))] + 1.0f) + 4e+02f));
			float fTemp3 = 1.0f / fTemp2;
			float fTemp4 = (fTemp3 + 1.0f) / fTemp2 + 1.0f;
			float fTemp5 = ((iTemp0) ? 0.0f : fSlow2 + fRec2[1]);
			fRec2[0] = fTemp5 - std::floor(fTemp5);
			float fTemp6 = 0.35f * ftbl0PadMotionSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec2[0]), 65535))];
			fVec2[0] = fSlow3;
			iRec3[0] = iSlow4 * (iRec3[1] + 1);
			fRec4[0] = fSlow3 + fRec4[1] * float(fVec2[1] >= fSlow3);
			float fTemp7 = fSlow8 + fRec7[1] + -1.0f;
			int iTemp8 = fTemp7 < 0.0f;
			float fTemp9 = fSlow8 + fRec7[1];
			fRec7[0] = ((iTemp8) ? fTemp9 : fTemp7);
			float fRec8 = ((iTemp8) ? fTemp9 : fSlow8 + fRec7[1] + fSlow9 * fTemp7);
			float fTemp10 = fSlow11 + fRec9[1] + -1.0f;
			int iTemp11 = fTemp10 < 0.0f;
			float fTemp12 = fSlow11 + fRec9[1];
			fRec9[0] = ((iTemp11) ? fTemp12 : fTemp10);
			float fRec10 = ((iTemp11) ? fTemp12 : fSlow11 + fRec9[1] + fSlow12 * fTemp10);
			float fTemp13 = fSlow14 + fRec11[1] + -1.0f;
			int iTemp14 = fTemp13 < 0.0f;
			float fTemp15 = fSlow14 + fRec11[1];
			fRec11[0] = ((iTemp14) ? fTemp15 : fTemp13);
			float fRec12 = ((iTemp14) ? fTemp15 : fSlow14 + fRec11[1] + fSlow15 * fTemp13);
			float fTemp16 = fSlow17 + fRec13[1] + -1.0f;
			int iTemp17 = fTemp16 < 0.0f;
			float fTemp18 = fSlow17 + fRec13[1];
			fRec13[0] = ((iTemp17) ? fTemp18 : fTemp16);
			float fRec14 = ((iTemp17) ? fTemp18 : fSlow17 + fRec13[1] + fSlow18 * fTemp16);
			float fTemp19 = 1.0f - (fRec14 + (fRec12 - (1.0f - (fRec10 + fRec8))));
			fVec3[0] = fTemp19;
			fRec6[0] = -((fRec6[1] * (1.0f - fTemp3) + 0.5f * (fTemp19 + fVec3[1])) / (fTemp3 + 1.0f));
			fRec5[0] = fRec6[0] - (fRec5[2] * ((fTemp3 + -1.0f) / fTemp2 + 1.0f) + 2.0f * fRec5[1] * (1.0f - 1.0f / PadMotion_faustpower2_f(fTemp2))) / fTemp4;
			float fTemp20 = (fRec5[2] + fRec5[0] + 2.0f * fRec5[1]) * std::max<float>(0.0f, std::min<float>(fConst5 * fRec4[0], std::max<float>(fConst6 * (fConst4 - fRec4[0]) + 1.0f, 0.8f)) * (1.0f - fConst3 * float(iRec3[0])));
			output0[i0] = FAUSTFLOAT(fSlow19 * (fTemp20 * std::sqrt(0.5f - fTemp6) / fTemp4));
			output1[i0] = FAUSTFLOAT(fSlow19 * (fTemp20 * std::sqrt(fTemp6 + 0.5f) / fTemp4));
			iVec1[1] = iVec1[0];
			fRec1[1] = fRec1[0];
			fRec2[1] = fRec2[0];
			fVec2[1] = fVec2[0];
			iRec3[1] = iRec3[0];
			fRec4[1] = fRec4[0];
			fRec7[1] = fRec7[0];
			fRec9[1] = fRec9[0];
			fRec11[1] = fRec11[0];
			fRec13[1] = fRec13[0];
			fVec3[1] = fVec3[0];
			fRec6[1] = fRec6[0];
			fRec5[2] = fRec5[1];
			fRec5[1] = fRec5[0];
		}
	}

};

#endif
